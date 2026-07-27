# arkkala/blog/serializers/category.py
from rest_framework import serializers
from blog.models.category import Category

class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug']