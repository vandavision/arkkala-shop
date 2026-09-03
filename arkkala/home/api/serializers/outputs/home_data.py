from typing import Optional
from rest_framework import serializers

from home.api.serializers.outputs.models import (
    StorySerializer,
    SliderSerializer,
    BannerSerializer,
    StoreReviewSerializer
)
from shop.models import Category as ShopCategory, Brand
from shop.serializers import ProductDetailSerializer
from blog.serializers import PostListSerializer


class SimpleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCategory
        fields: list[str] = ['uuid', 'title', 'slug', 'image']


class HomeBrandSerializer(serializers.ModelSerializer):

    logo = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = '__all__'

    def get_logo(self, obj: Brand) -> Optional[str]:
        request = self.context.get('request')
        img_field = getattr(obj, 'logo', None) or getattr(obj, 'image', None) or getattr(obj, 'icon', None)
        
        if img_field and hasattr(img_field, 'url'):
            try:
                return request.build_absolute_uri(img_field.url) if request else img_field.url
            except ValueError:
                return None
        return None


class HomePageDataOutputSerializer(serializers.Serializer):
    stories = StorySerializer(many=True)
    sliders = SliderSerializer(many=True)
    banners = BannerSerializer(many=True)
    categories = SimpleCategorySerializer(many=True)
    special_offers = ProductDetailSerializer(many=True)
    best_sellers = ProductDetailSerializer(many=True)
    brands = HomeBrandSerializer(many=True)
    store_reviews = StoreReviewSerializer(many=True)
    latest_posts = PostListSerializer(many=True)