# arkkala/blog/serializers/tag.py
from rest_framework import serializers
from blog.models.tag import Tag

class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    class Meta:
        model = Tag
        fields = ['uuid', 'title', 'slug']