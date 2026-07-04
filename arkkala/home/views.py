"""
Aggregator API View for the Home Page.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Story, Slider, Banner, StoreReview
from .serializers import StorySerializer, SliderSerializer, BannerSerializer, StoreReviewSerializer, SimpleCategorySerializer

from shop.models import Product, Brand, Category
from shop.serializers import ProductDetailSerializer, BrandSerializer
from blog.models import Post
from blog.serializers import PostListSerializer


class HomePageDataView(APIView):
    """
    Returns all necessary data for the Home Page in a single aggregated JSON.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # 1. Home CMS Elements
        stories = Story.objects.filter(is_active=True)
        sliders = Slider.objects.filter(is_active=True)
        banners = Banner.objects.filter(is_active=True)
        store_reviews = StoreReview.objects.filter(is_active=True)[:10]

        # 2. Shop Data
        categories = Category.objects.filter(is_active=True, parent__isnull=True)[:10]
        brands = Brand.objects.filter(is_active=True)[:10]
        
        special_offers = Product.objects.filter(is_active=True).order_by('-view_count')[:10]
        
        best_sellers = Product.objects.filter(is_active=True).order_by('-sold_count')[:10]

        # 3. Blog Data
        latest_posts = Post.objects.filter(is_published=True).order_by('-created_at')[:6]

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

        return Response(data)