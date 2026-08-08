from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog.api.views.post import PostViewSet
from blog.api.views.category import BlogCategoryViewSet

router = DefaultRouter()
router.register(r'categories', BlogCategoryViewSet, basename='blog-category')
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
]