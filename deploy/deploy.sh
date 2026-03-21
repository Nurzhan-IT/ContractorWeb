#!/bin/bash
# deploy.sh — Pull latest code and restart the app
# Usage: sudo bash deploy.sh

set -euo pipefail

APP_DIR="/var/www/contractorwebdev/website_django"
VENV="$APP_DIR/../venv"
ENV_FILE="$APP_DIR/../.env"
SERVICE="contractorwebdev"

# Load .env so production.py can read SECRET_KEY, DATABASE_URL, etc.
if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
else
    echo "ERROR: .env not found at $ENV_FILE" >&2
    exit 1
fi

export DJANGO_SETTINGS_MODULE=config.settings.production

echo "==> Pulling latest code..."
git -C "$APP_DIR" pull origin main

echo "==> Installing/updating dependencies..."
"$VENV/bin/pip" install -q -r "$APP_DIR/requirements.txt"

echo "==> Collecting static files..."
"$VENV/bin/python" "$APP_DIR/manage.py" collectstatic --noinput

echo "==> Applying migrations..."
"$VENV/bin/python" "$APP_DIR/manage.py" migrate --noinput

echo "==> Reloading gunicorn (zero-downtime)..."
systemctl reload "$SERVICE"

echo "==> Done. Status:"
systemctl status "$SERVICE" --no-pager -l
