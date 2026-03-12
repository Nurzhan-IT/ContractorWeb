import os
import urllib.parse

from .base import *  # noqa: F401, F403

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Parse DATABASE_URL (postgresql://user:pass@host:port/dbname)
# Requires psycopg2-binary: pip install psycopg2-binary
_db_url = os.environ['DATABASE_URL']
_parsed = urllib.parse.urlparse(_db_url)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _parsed.path.lstrip('/'),
        'USER': _parsed.username or '',
        'PASSWORD': _parsed.password or '',
        'HOST': _parsed.hostname or 'localhost',
        'PORT': _parsed.port or 5432,
        'OPTIONS': {'sslmode': 'require'},
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
