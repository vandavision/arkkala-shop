"""
Serializers for Home Page data.
"""
from typing import Optional
from rest_framework import serializers
from .models import Story, Slider, Banner, StoreReview, SiteSetting, AboutPage, FAQ
from shop.models import Category as ShopCategory

from shop.serializers import ProductDetailSerializer, BrandSerializer
from blog.serializers import PostListSerializer, BlogCategorySerializer
from .models import ContactMessage

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
        fields = ['uuid', 'title', 'slug', 'image']


class SiteSettingSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    namad_1_img_url = serializers.SerializerMethodField()
    namad_2_img_url = serializers.SerializerMethodField()
    namad_3_img_url = serializers.SerializerMethodField()
    namad_4_img_url = serializers.SerializerMethodField()
    namad_5_img_url = serializers.SerializerMethodField()
    namad_6_img_url = serializers.SerializerMethodField()
    namad_7_img_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSetting
        fields = '__all__'

    def _get_image_url(self, image_field) -> Optional[str]:
        """Safely retrieve absolute URL for an ImageField to avoid ValueErrors on empty fields."""
        request = self.context.get('request')
        if image_field and hasattr(image_field, 'url'):
            try:
                return request.build_absolute_uri(image_field.url) if request else image_field.url
            except ValueError:
                return None
        return None

    def get_logo_url(self, obj: SiteSetting) -> Optional[str]: 
        return self._get_image_url(obj.logo)

    def get_namad_1_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_1_img)
    def get_namad_2_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_2_img)
    def get_namad_3_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_3_img)
    def get_namad_4_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_4_img)
    def get_namad_5_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_5_img)
    def get_namad_6_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_6_img)
    def get_namad_7_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_7_img)


class FAQSerializer(serializers.ModelSerializer):
    """
    Serializer for Frequently Asked Questions.
    """
    class Meta:
        model = FAQ
        fields = ['uuid', 'question', 'answer', 'order']


class AboutPageSerializer(serializers.ModelSerializer):
    """
    Serializer for the dynamic About Us page content.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutPage
        fields = ['uuid', 'title', 'content', 'image_url']

    def get_image_url(self, obj: AboutPage) -> Optional[str]:
        """
        Safely builds the absolute URI for the about page image.
        """
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            try:
                return request.build_absolute_uri(obj.image.url) if request else obj.image.url
            except ValueError:
                return None
        return None


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for handling incoming contact us data."""
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'phone_number', 'email', 'subject', 'message']