# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: Python dependencies, built into an isolated venv
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# build-essential covers any dependency without a prebuilt wheel for this
# platform/Python combo; it never reaches the runtime image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt


# ---------------------------------------------------------------------------
# Stage 2: Tailwind CSS build (Linux CLI binary, mirrors build_tailwind.ps1)
# ---------------------------------------------------------------------------
FROM debian:bookworm-slim AS tailwind

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sL -o /usr/local/bin/tailwindcss \
       https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.19/tailwindcss-linux-x64 \
    && chmod +x /usr/local/bin/tailwindcss

WORKDIR /app
# Only what tailwind.config.js needs to scan for class names, plus the
# input stylesheet — keeps this stage's cache independent of app code.
COPY tailwind.config.js .
COPY static/css/tailwind_input.css static/css/tailwind_input.css
COPY templates templates
COPY static/js static/js
COPY apps apps

RUN tailwindcss -i static/css/tailwind_input.css -o static/css/tailwind.css --minify


# ---------------------------------------------------------------------------
# Stage 3: Runtime image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production

# libmagic1 is required at runtime by python-magic.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /usr/sbin/nologin --create-home appuser

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY . .
# Overwrite the committed CSS with the freshly compiled one from Stage 2.
COPY --from=tailwind /app/static/css/tailwind.css static/css/tailwind.css

# collectstatic only reads files and writes to STATIC_ROOT — it never opens
# a DB connection, so build-time placeholders for the required settings are
# safe and are not baked into the final image (scoped to this RUN only).
RUN mkdir -p /app/media /app/staticfiles \
    && chmod +x docker/entrypoint.sh \
    && SECRET_KEY=build-time-placeholder \
       DATABASE_URL=postgresql://build:build@localhost:5432/build \
       ALLOWED_HOSTS=localhost \
       python manage.py collectstatic --noinput \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=3).status == 200 else 1)"

# entrypoint.sh waits for Postgres, runs migrations, and (in production)
# collectstatic, then hands off to CMD via `exec "$@"`. Invoked via `sh`
# (not exec form) so it still runs when /app is bind-mounted over a source
# tree whose executable bit didn't survive (e.g. checked out on Windows).
ENTRYPOINT ["sh", "docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
