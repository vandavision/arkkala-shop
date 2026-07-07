"""
Base Django settings for arkkala project.
"""
import os
from pathlib import Path
from corsheaders.defaults import default_headers

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

SECRET_KEY: str = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-arkkala-default-key')

INSTALLED_APPS: list[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'corsheaders',
    'rest_framework',
    'platform_painless',
    'platform_tools',
    'platform_seo',
    'django_jsonform',

    'rest_framework_simplejwt',
    'users',
    'shop',
    'orders',
    'payments',
    'blog',
    'search',
    'home',
]

MIDDLEWARE: list[str] = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF: str = 'arkkala.urls'

TEMPLATES: list[dict] = [
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

WSGI_APPLICATION: str = 'arkkala.wsgi.application'

AUTH_PASSWORD_VALIDATORS: list[dict] = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE: str = 'fa-ir'
TIME_ZONE: str = 'Asia/Tehran'
USE_I18N: bool = True
USE_TZ: bool = True

DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

WSGI_APPLICATION: str = 'arkkala.wsgi.application'
ASGI_APPLICATION: str = 'arkkala.asgi.application'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

AUTH_USER_MODEL = 'users.User'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@arkkala.com'
VAT_RATE = 0

CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-guest-id',
]

CORS_ALLOW_ALL_ORIGINS = True

# Authentication Mode: 'OTP' or 'EMAIL'
AUTH_MODE: str = os.environ.get('AUTH_MODE', 'EMAIL')  # Default to EMAIL if not set

# Kavenegar SMS Configuration
KAVENEGAR_API_KEY: str = os.environ.get('KAVENEGAR_API_KEY', 'your_kavenegar_api_key_here')
KAVENEGAR_OTP_TEMPLATE: str = os.environ.get('KAVENEGAR_OTP_TEMPLATE', 'verify')

# Rate Limiting for SMS (Security)
OTP_WAIT_TIME_MINUTES: int = 2
OTP_MAX_DAILY_REQUESTS: int = 5