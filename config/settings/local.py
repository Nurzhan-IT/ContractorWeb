import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *  # noqa: F401, F403

# Load .env from project root
load_dotenv(BASE_DIR / '.env')  # noqa: F405

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
