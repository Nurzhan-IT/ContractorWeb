import os
import urllib.parse

from .base import *  # noqa: F401, F403

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Trusted origins for CSRF (required for HTTPS + Cloudflare proxy)
CSRF_TRUSTED_ORIGINS = [
    f'https://{h.strip()}'
    for h in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if h.strip()
]

# Parse DATABASE_URL (postgresql://user:pass@host:port/dbname)
# Requires psycopg2-binary: pip install psycopg2-binary
_db_url = os.environ['DATABASE_URL']
_parsed = urllib.parse.urlparse(_db_url)

# sslmode=prefer works for local PostgreSQL (no SSL) and remote (with SSL)
_sslmode = urllib.parse.parse_qs(_parsed.query).get('sslmode', ['prefer'])[0]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _parsed.path.lstrip('/'),
        'USER': _parsed.username or '',
        'PASSWORD': _parsed.password or '',
        'HOST': _parsed.hostname or 'localhost',
        'PORT': _parsed.port or 5432,
        'OPTIONS': {'sslmode': _sslmode},
        'CONN_MAX_AGE': 60,
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405

# Whitenoise: insert after SecurityMiddleware for static file serving
MIDDLEWARE = [  # noqa: F405
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'config.middleware.EnsureCsrfCookieMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cache (LocMem for single-process; switch to Redis for multi-worker)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000        # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Clickjacking / content sniffing
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True  # Deprecated in Django 4.0+ but harmless
