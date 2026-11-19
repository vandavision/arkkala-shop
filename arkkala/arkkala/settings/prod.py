import os
from .base import *

DEBUG: bool = False

ALLOWED_HOSTS: list[str] = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()
] + ['localhost', '127.0.0.1', 'django']

CORS_ALLOWED_ORIGINS: list[str] = [
    o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()
]
CORS_ALLOW_CREDENTIALS: bool = True

CSRF_TRUSTED_ORIGINS: list[str] = [
    o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]

DATABASES: dict = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

CACHES: dict = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
    }
}

CELERY_BROKER_URL: str = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND: str = os.environ.get('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT: list[str] = ['json']
CELERY_TASK_SERIALIZER: str = 'json'

STATIC_URL: str = '/staticfiles/'
STATIC_ROOT: Path = BASE_DIR / 'staticfiles'

MEDIA_URL: str = '/media/'
MEDIA_ROOT: Path = BASE_DIR / 'mediafiles'

SECURE_PROXY_SSL_HEADER: tuple[str, str] = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST: bool = True
SECURE_SSL_REDIRECT: bool = True
SECURE_REDIRECT_EXEMPT: list[str] = [r'^healthz/$']
SESSION_COOKIE_SECURE: bool = True
CSRF_COOKIE_SECURE: bool = True
SECURE_HSTS_SECONDS: int = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
SECURE_HSTS_PRELOAD: bool = True