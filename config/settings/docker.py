import os
import urllib.parse

from .local import *  # noqa: F401, F403

# Same dev-friendly defaults as local.py (DEBUG=True, permissive ALLOWED_HOSTS,
# CSRF_TRUSTED_ORIGINS), except the database points at the `db` Compose
# service instead of the SQLite file local.py uses outside Docker.
_db_url = os.environ['DATABASE_URL']
_parsed = urllib.parse.urlparse(_db_url)
_sslmode = urllib.parse.parse_qs(_parsed.query).get('sslmode', ['disable'])[0]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _parsed.path.lstrip('/'),
        'USER': _parsed.username or '',
        'PASSWORD': _parsed.password or '',
        'HOST': _parsed.hostname or 'db',
        'PORT': _parsed.port or 5432,
        'OPTIONS': {'sslmode': _sslmode} if _sslmode != 'disable' else {},
    }
}
