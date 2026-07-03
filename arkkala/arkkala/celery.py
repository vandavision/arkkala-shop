"""
Celery configuration for the arkkala project.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkkala.settings.dev')

app: Celery = Celery('arkkala')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()