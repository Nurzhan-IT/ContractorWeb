#!/bin/bash
# deploy.sh — Pull latest code and restart the app
# Run from /var/www/contractorwebdev/website_django as root or sudo

set -euo pipefail

APP_DIR="/var/www/contractorwebdev/website_django"
VENV="$APP_DIR/../venv"
SERVICE="contractorwebdev"

echo "==> Pulling latest code..."
git -C "$APP_DIR" pull origin main

echo "==> Installing/updating dependencies..."
"$VENV/bin/pip" install -q -r "$APP_DIR/requirements.txt"

echo "==> Collecting static files..."
DJANGO_SETTINGS_MODULE=config.settings.production \
    "$VENV/bin/python" "$APP_DIR/manage.py" collectstatic --noinput

echo "==> Applying migrations..."
DJANGO_SETTINGS_MODULE=config.settings.production \
    "$VENV/bin/python" "$APP_DIR/manage.py" migrate --noinput

echo "==> Reloading gunicorn (zero-downtime)..."
systemctl reload "$SERVICE"

echo "==> Done. Status:"
systemctl status "$SERVICE" --no-pager -l
