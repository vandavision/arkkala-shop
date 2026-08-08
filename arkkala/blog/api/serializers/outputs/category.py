from rest_framework import serializers
from blog.models.category import Category

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug']