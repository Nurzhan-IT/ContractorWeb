#!/bin/bash
# deploy.sh — Pull latest code and restart the app
# Usage: sudo bash deploy.sh

set -euo pipefail

APP_DIR="/var/www/contractorwebdev/website_django"
VENV="$APP_DIR/../venv"
SERVICE="contractorwebdev"

# .env is NOT sourced here — production.py loads it automatically via python-dotenv.
# Sourcing .env in bash breaks when SECRET_KEY contains special characters (^, #, %).
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
