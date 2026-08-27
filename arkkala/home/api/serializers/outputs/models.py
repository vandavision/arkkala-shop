from typing import Optional
from rest_framework import serializers
from home.models import Story, Slider, Banner, StoreReview

class StorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Story model.
    """
    class Meta:
        model = Story
        fields: list[str] = ['uuid', 'title', 'image', 'video', 'link']

class SliderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Slider model.
    """
    class Meta:
        model = Slider
        fields: list[str] = ['uuid', 'title', 'image', 'link']

class BannerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Banner model.
    """
    class Meta:
        model = Banner
        fields: list[str] = ['uuid', 'title', 'image', 'link', 'position']

class StoreReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the StoreReview model.
    """
    class Meta:
        model = StoreReview
        fields: list[str] = ['uuid', 'user_name', 'body', 'created_at']