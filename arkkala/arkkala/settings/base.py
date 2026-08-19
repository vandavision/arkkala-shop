import os
from pathlib import Path
from corsheaders.defaults import default_headers

os.environ["GIT_PYTHON_REFRESH"] = "quiet"

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

SECRET_KEY: str = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-arkkala-default-key')

DJANGO_ADMIN_URL_PREFIX: str = 'admin'

INSTALLED_APPS: list[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    'corsheaders',
    'rest_framework',
    'platform_painless',
    'platform_tools',
    'platform_seo',
    'django_jsonform',
    'drf_spectacular',

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
ASGI_APPLICATION: str = 'arkkala.asgi.application'

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

REST_FRAMEWORK: dict = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'users.api.exceptions.custom_exception_handler',
}

SPECTACULAR_SETTINGS: dict = {
    'TITLE': 'Arkkala Enterprise API',
    'DESCRIPTION': 'CQRS and Event-Driven E-Commerce API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

AUTH_USER_MODEL: str = 'users.User'

EMAIL_BACKEND: str = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL: str = 'noreply@arkkala.com'
VAT_RATE: int = 0

CORS_ALLOW_HEADERS: list[str] = list(default_headers) + [
    'x-guest-id',
]

AUTH_MODE: str = os.environ.get('AUTH_MODE', 'EMAIL')

KAVENEGAR_API_KEY: str = os.environ.get('KAVENEGAR_API_KEY', 'your_kavenegar_api_key_here')
KAVENEGAR_OTP_TEMPLATE: str = os.environ.get('KAVENEGAR_OTP_TEMPLATE', 'verify')

OTP_WAIT_TIME_MINUTES: int = 2
OTP_MAX_DAILY_REQUESTS: int = 5