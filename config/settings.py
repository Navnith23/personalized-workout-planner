"""
Django settings for the Personalized Fitness & Lifestyle Planner.

SECURITY CHECKLIST
==================
Deployment (PythonAnywhere) must set the following environment variables
in the WSGI configuration file or via the web dashboard:

  DJANGO_SECRET_KEY   — a long random string (generate with:
                         python -c "import secrets; print(secrets.token_hex(50))")
  DJANGO_DEBUG        — set to "False" in production
  DJANGO_ALLOWED_HOSTS — comma-separated list, e.g. "navnith23.pythonanywhere.com"

Do NOT commit a real secret key to version control.
"""
import os
import importlib.util
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security settings
# ---------------------------------------------------------------------------

_raw_secret = os.environ.get('DJANGO_SECRET_KEY', '')
if not _raw_secret:
    import warnings
    warnings.warn(
        "DJANGO_SECRET_KEY is not set. Using a default is ONLY acceptable in "
        "local development. Set the environment variable before deploying.",
        stacklevel=1,
    )
    _raw_secret = 'dev-only-secret-key-do-not-use-in-production-!!!'
SECRET_KEY = _raw_secret

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').strip().lower() in ('true', '1', 'yes')

_raw_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = (
    [h.strip() for h in _raw_hosts.split(',') if h.strip()]
    if _raw_hosts
    else (['localhost', '127.0.0.1'] if DEBUG else [])
)

# HTTPS / cookie security — always on in production, off in local dev
SESSION_COOKIE_SECURE   = not DEBUG
CSRF_COOKIE_SECURE      = not DEBUG
SECURE_SSL_REDIRECT     = not DEBUG
SECURE_HSTS_SECONDS     = 0 if DEBUG else 31536000   # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD     = not DEBUG

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'accounts',
    'assessment',
    'exercises',
    'programs',
    'progress',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
ASGI_APPLICATION = 'config.asgi.application'

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
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

if importlib.util.find_spec('whitenoise'):
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'assessment:dashboard_redirect'
LOGOUT_REDIRECT_URL = 'accounts:login'

# ---------------------------------------------------------------------------
# Email — password reset
# ---------------------------------------------------------------------------
# For PythonAnywhere, configure SMTP via environment variables.
# Example: Gmail SMTP (replace with real credentials, never commit them).
#
#   EMAIL_BACKEND  = 'django.core.mail.backends.smtp.EmailBackend'
#   EMAIL_HOST     = 'smtp.gmail.com'
#   EMAIL_PORT     = 587
#   EMAIL_USE_TLS  = True
#   EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
#   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
#
# Until SMTP is configured on PythonAnywhere, use the console backend so
# password-reset emails print to the server log (safe for dev/staging).
EMAIL_BACKEND = os.environ.get(
    'DJANGO_EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1')
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@fitplanner.example.com')
