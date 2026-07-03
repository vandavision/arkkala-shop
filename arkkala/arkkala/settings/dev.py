"""
Development settings for arkkala project.
"""
from .base import *
import os

DEBUG: bool = True

ALLOWED_HOSTS: list[str] = ['*']

DATABASES: dict = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'arkkala_db'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': 'postgres',
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

CELERY_BROKER_URL: str = "redis://redis:6379/0"
CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

STATIC_URL: str = 'static/'
STATIC_ROOT: Path = BASE_DIR / 'staticfiles'

MEDIA_URL: str = 'media/'
MEDIA_ROOT: Path = BASE_DIR / 'mediafiles'

CORS_ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS: bool = True