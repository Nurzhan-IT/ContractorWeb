import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing base so env vars are available when base.py runs
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BASE_DIR / '.env')

from .base import *  # noqa: F401, F403

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-local-dev-only-do-not-use-in-production',
)

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}
