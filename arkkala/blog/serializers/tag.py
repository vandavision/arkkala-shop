from rest_framework import serializers
from blog.models.tag import Tag

class TagSerializer(serializers.ModelSerializer):
    """
    Exposes minimal metadata structures reliably defining explicit field layouts.
    """
    class Meta:
        model = Tag
        fields: list = ['uuid', 'title', 'slug']