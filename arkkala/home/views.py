# arkkala/arkkala/home/views.py

"""
API Views for the home application.
"""
from typing import Dict, Any
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework import status

from .serializers import (
    StorySerializer,
    SliderSerializer,
    BannerSerializer,
    StoreReviewSerializer,
    SimpleCategorySerializer,
    SiteSettingSerializer,
    FAQSerializer,
    AboutPageSerializer,
    ContactMessageSerializer
)
from shop.serializers import ProductDetailSerializer, BrandSerializer
from blog.serializers import PostListSerializer
from .services import HomeService


class HomePageDataView(APIView):
    """
    Returns all necessary data for the Home Page in a single aggregated JSON.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        cache_key: str = "home_page_aggregated_data"
        cached_data: Dict[str, Any] | None = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        raw_data: Dict[str, Any] = HomeService.get_home_page_data()
        ctx: Dict[str, Request] = {'request': request}

        serialized_data: Dict[str, Any] = {
            'stories': StorySerializer(raw_data['stories'], many=True, context=ctx).data,
            'sliders': SliderSerializer(raw_data['sliders'], many=True, context=ctx).data,
            'banners': BannerSerializer(raw_data['banners'], many=True, context=ctx).data,
            'categories': SimpleCategorySerializer(raw_data['categories'], many=True, context=ctx).data,
            'special_offers': ProductDetailSerializer(raw_data['special_offers'], many=True, context=ctx).data,
            'best_sellers': ProductDetailSerializer(raw_data['best_sellers'], many=True, context=ctx).data,
            'brands': BrandSerializer(raw_data['brands'], many=True, context=ctx).data,
            'store_reviews': StoreReviewSerializer(raw_data['store_reviews'], many=True, context=ctx).data,
            'latest_posts': PostListSerializer(raw_data['latest_posts'], many=True, context=ctx).data,
        }

        cache.set(cache_key, serialized_data, timeout=600)
        return Response(serialized_data, status=status.HTTP_200_OK)


class SiteSettingView(APIView):
    """
    API View to retrieve the global site settings.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        setting = HomeService.get_site_settings()
        serializer = SiteSettingSerializer(setting, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FAQListView(APIView):
    """
    API View to retrieve all active Frequently Asked Questions.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        faqs = HomeService.get_faqs()
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AboutPageDetailView(APIView):
    """
    API View to fetch the latest active dynamic content for the About Us page.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        about_content = HomeService.get_about_us()
        if not about_content:
            return Response(
                {
                    "title": "درباره ما",
                    "content": "محتوایی برای این صفحه ثبت نشده است.",
                    "image_url": None
                },
                status=status.HTTP_200_OK
            )
        serializer = AboutPageSerializer(about_content, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContactMessageAPIView(APIView):
    """
    API Endpoint for receiving contact messages from frontend.
    """
    permission_classes: list = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        HomeService.create_contact_message(serializer.validated_data)
        return Response(
            {"message": "پیام شما با موفقیت دریافت شد."},
            status=status.HTTP_201_CREATED
        )