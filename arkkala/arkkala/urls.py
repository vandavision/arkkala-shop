"""
Main URL configuration for arkkala.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from typing import Any

urlpatterns: list[Any] = [
    path('admin/', admin.site.urls),
    path('api/shop/', include('shop.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)