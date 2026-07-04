"""
Serializers for Home Page data.
"""
from rest_framework import serializers
from .models import Story, Slider, Banner, StoreReview
from shop.models import Category as ShopCategory

from shop.serializers import ProductDetailSerializer, BrandSerializer
from blog.serializers import PostListSerializer, BlogCategorySerializer


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['uuid', 'title', 'image', 'video', 'link']

class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = ['uuid', 'title', 'image', 'link']

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['uuid', 'title', 'image', 'link', 'position']

class StoreReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreReview
        fields = ['uuid', 'user_name', 'body', 'created_at']

class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCategory
        fields = ['uuid', 'title', 'slug']