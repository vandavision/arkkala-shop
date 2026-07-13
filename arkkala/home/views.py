from django.utils import timezone
from django.db.models import Prefetch
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView

from .models import Story, Slider, Banner, StoreReview, SiteSetting, AboutPage, FAQ
from .serializers import (
    StorySerializer, 
    SliderSerializer, 
    BannerSerializer, 
    StoreReviewSerializer, 
    SimpleCategorySerializer,
    SiteSettingSerializer,
    FAQSerializer,
    AboutPageSerializer
)

from shop.models import Product, Brand, Category as ShopCategory, Comment as ShopComment, Question as ShopQuestion
from shop.serializers import ProductDetailSerializer, BrandSerializer
from blog.models import Post, Comment as BlogComment
from blog.serializers import PostListSerializer


class HomePageDataView(APIView):
    """
    Returns all necessary data for the Home Page in a single aggregated JSON.
    Uses deep prefetching and Redis caching to eliminate N+1 queries entirely.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # We cache the entire heavy home page response for 10 minutes
        cache_key = "home_page_aggregated_data"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        now = timezone.now()

        # 1. Home CMS Elements
        stories = Story.objects.filter(is_active=True)
        sliders = Slider.objects.filter(is_active=True)
        banners = Banner.objects.filter(is_active=True)
        store_reviews = StoreReview.objects.filter(is_active=True)[:10]

        # 2. Shop Base Data
        categories = ShopCategory.objects.filter(is_active=True, parent__isnull=True)[:10]
        brands = Brand.objects.filter(is_active=True)[:10]

        # Heavy Prefetch Object for Products to prevent N+1 in ProductDetailSerializer
        product_prefetch = [
            'variants__attribute_values',
            'gallery',
            'videos',
            'price_history',
            Prefetch('comments', queryset=ShopComment.objects.filter(is_approved=True), to_attr='approved_comments'),
            Prefetch('questions', queryset=ShopQuestion.objects.filter(is_approved=True), to_attr='approved_questions')
        ]
        
        special_offers = Product.objects.filter(
            is_active=True,
            special_discount_percent__gt=0,
            special_offer_end__isnull=False,
            special_offer_end__gt=now
        ).select_related('brand', 'category').prefetch_related(*product_prefetch).order_by('special_offer_end')[:10]
        
        best_sellers = Product.objects.filter(
            is_active=True
        ).select_related('brand', 'category').prefetch_related(*product_prefetch).order_by('-sold_count')[:10]

        # 3. Blog Data (Optimized with Select/Prefetch)
        latest_posts = Post.objects.filter(is_published=True).select_related('category', 'author').prefetch_related(
            'tags',
            Prefetch('comments', queryset=BlogComment.objects.filter(is_approved=True), to_attr='approved_comments')
        ).order_by('-created_at')[:6]

        ctx = {'request': request}

        # Serialization
        data = {
            'stories': StorySerializer(stories, many=True, context=ctx).data,
            'sliders': SliderSerializer(sliders, many=True, context=ctx).data,
            'banners': BannerSerializer(banners, many=True, context=ctx).data,
            'categories': SimpleCategorySerializer(categories, many=True, context=ctx).data,
            'special_offers': ProductDetailSerializer(special_offers, many=True, context=ctx).data,
            'best_sellers': ProductDetailSerializer(best_sellers, many=True, context=ctx).data,
            'brands': BrandSerializer(brands, many=True, context=ctx).data,
            'store_reviews': StoreReviewSerializer(store_reviews, many=True, context=ctx).data,
            'latest_posts': PostListSerializer(latest_posts, many=True, context=ctx).data,
        }

        # Cache the result for 600 seconds (10 minutes)
        cache.set(cache_key, data, timeout=600)

        return Response(data)


class SiteSettingView(APIView):
    """
    API View to retrieve the global site settings.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        setting = SiteSetting.load()
        serializer = SiteSettingSerializer(setting, context={'request': request})
        return Response(serializer.data)


class FAQListView(ListAPIView):
    """
    API View to retrieve all active Frequently Asked Questions.
    """
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]


class AboutPageDetailView(APIView):
    """
    API View to fetch the latest active dynamic content for the About Us page.
    """
    permission_classes = [AllowAny]

    def get(self, request) -> Response:
        """
        Handles GET requests and returns the first active AboutPage content.
        """
        about_content = AboutPage.objects.filter(is_active=True).first()
        if not about_content:
            return Response(
                {
                    "title": "درباره ما", 
                    "content": "محتوایی برای این صفحه ثبت نشده است.", 
                    "image_url": None
                }, 
                status=200
            )
        serializer = AboutPageSerializer(about_content, context={'request': request})
        return Response(serializer.data)