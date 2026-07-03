"""
WSGI config for arkkala project.
"""
import os
from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkkala.settings.prod')

application: WSGIHandler = get_wsgi_application()