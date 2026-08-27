from rest_framework import serializers

from home.api.serializers.outputs.models import (
    StorySerializer,
    SliderSerializer,
    BannerSerializer,
    StoreReviewSerializer
)
from shop.models import Category as ShopCategory
from shop.serializers import ProductDetailSerializer, BrandSerializer
from blog.serializers import PostListSerializer


class SimpleCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for projecting shop categories on the home page.
    """
    class Meta:
        model = ShopCategory
        fields: list[str] = ['uuid', 'title', 'slug', 'image']


class HomePageDataOutputSerializer(serializers.Serializer):
    """
    Output serializer mapping the aggregated home page DTO/QuerySet results.
    """
    stories = StorySerializer(many=True)
    sliders = SliderSerializer(many=True)
    banners = BannerSerializer(many=True)
    categories = SimpleCategorySerializer(many=True)
    special_offers = ProductDetailSerializer(many=True)
    best_sellers = ProductDetailSerializer(many=True)
    brands = BrandSerializer(many=True)
    store_reviews = StoreReviewSerializer(many=True)
    latest_posts = PostListSerializer(many=True)