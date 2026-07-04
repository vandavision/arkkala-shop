"""
URLs mapping for Blog App.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, BlogCategoryViewSet

router = DefaultRouter()
router.register(r'categories', BlogCategoryViewSet, basename='blog-category')
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
]