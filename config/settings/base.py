import os
import sys
from pathlib import Path

# Build paths inside the project: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Make all apps importable as top-level modules (e.g. `import quote` instead of `import apps.quote`)
sys.path.insert(0, str(BASE_DIR / 'apps'))

SECRET_KEY = 'django-insecure-base-key-override-in-local-or-production'

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django_jinja',
    # Project apps (resolved via apps/ on sys.path)
    'demo',
    'landing',
    'quote',
    'emergency',
    'service_area',
    'portfolio',
    'booking',
    'web_quote',
    'blog',
    'apps.plumbing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'config.middleware.EnsureCsrfCookieMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        # Jinja2 backend — handles all project .html templates in templates/
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'match_extension': '.html',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        # Django backend — handles admin and any Django-native templates
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Default database — overridden in local.py / production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OpenRouter AI (used by quote app)
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
OPENROUTER_MODEL = 'google/gemini-2.5-flash-lite'

# Cloudflare Turnstile (used by web_quote form on landing page)
# Default test keys always pass — replace with real keys from dash.cloudflare.com → Turnstile
CF_TURNSTILE_SITE_KEY   = os.environ.get('CF_TURNSTILE_SITE_KEY',   '1x00000000000000000000AA')
CF_TURNSTILE_SECRET_KEY = os.environ.get('CF_TURNSTILE_SECRET_KEY', '1x0000000000000000000000000000000AA')

# Cal.com (used by booking app)
CAL_API_KEY  = os.environ.get('CAL_API_KEY', '')
CAL_USERNAME = os.environ.get('CAL_USERNAME', 'demo')
CAL_BASE_URL = 'https://api.cal.com/v2'
CAL_SLUGS = {
    'plumbing_leak': os.environ.get('CAL_SLUG_PLUMBING',   'plumbing-repair'),
    'faucet_toilet': os.environ.get('CAL_SLUG_FAUCET',     'faucet-toilet'),
    'electrical':    os.environ.get('CAL_SLUG_ELECTRICAL', 'electrical-work'),
}
