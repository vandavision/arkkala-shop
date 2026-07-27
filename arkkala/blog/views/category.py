# arkkala/blog/views/category.py
from rest_framework import viewsets
from blog.models.category import Category
from blog.serializers.category import BlogCategorySerializer

class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for Blog Categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = BlogCategorySerializer
    pagination_class = None
    lookup_field = 'slug'