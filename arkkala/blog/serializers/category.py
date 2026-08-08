from rest_framework import serializers
from blog.models.category import Category

class BlogCategorySerializer(serializers.ModelSerializer):
    """
    Translates Domain mapping rules resolving safely to API representations.
    """
    class Meta:
        model = Category
        fields: list = ['uuid', 'title', 'slug']