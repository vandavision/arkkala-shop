"""
Production settings for arkkala project.
"""
from .base import *
import os

DEBUG: bool = False

ALLOWED_HOSTS: list[str] = ['api.arkkala.com', 'arkkala_prod_django']

CORS_ALLOWED_ORIGINS: list[str] = [
    "https://arkkala.com",
    "https://www.arkkala.com",
]
CORS_ALLOW_CREDENTIALS: bool = True

DATABASES: dict = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'postgres',
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

CELERY_BROKER_URL: str = "redis://redis:6379/0"
CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT: list[str] = ['json']
CELERY_TASK_SERIALIZER: str = 'json'

STATIC_URL: str = '/staticfiles/'
STATIC_ROOT: Path = BASE_DIR / 'staticfiles'

MEDIA_URL: str = '/media/'
MEDIA_ROOT: Path = BASE_DIR / 'mediafiles'

SECURE_PROXY_SSL_HEADER: tuple[str, str] = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT: bool = True
SESSION_COOKIE_SECURE: bool = True
CSRF_COOKIE_SECURE: bool = True
SECURE_HSTS_SECONDS: int = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
SECURE_HSTS_PRELOAD: bool = True