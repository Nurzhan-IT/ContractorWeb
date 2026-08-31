#!/bin/sh
set -e

wait_for_postgres() {
    python - <<'PY'
import os
import sys
import time
import urllib.parse

db_url = os.environ.get("DATABASE_URL", "")
if not db_url.startswith(("postgres://", "postgresql://")):
    # SQLite or unset — nothing to wait for.
    sys.exit(0)

import psycopg2

parsed = urllib.parse.urlparse(db_url)
max_attempts = 30

for attempt in range(1, max_attempts + 1):
    try:
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip("/"),
            user=parsed.username or "",
            password=parsed.password or "",
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
            connect_timeout=3,
        )
        conn.close()
        print("Postgres is up.")
        sys.exit(0)
    except psycopg2.OperationalError as exc:
        print(f"Postgres not ready yet ({attempt}/{max_attempts}): {exc}", file=sys.stderr)
        time.sleep(2)

print("Postgres did not become ready in time.", file=sys.stderr)
sys.exit(1)
PY
}

wait_for_postgres

python manage.py migrate --noinput

if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
    python manage.py collectstatic --noinput
fi

exec "$@"
