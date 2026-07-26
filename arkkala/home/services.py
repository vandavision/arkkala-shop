# arkkala/arkkala/home/services.py

"""
Service layer for the home application business logic.
"""
from typing import Dict, Any, Optional
from django.utils import timezone
from django.db.models import Prefetch, QuerySet

from .models import Story, Slider, Banner, StoreReview, SiteSetting, AboutPage, FAQ, ContactMessage
from shop.models import Product, Brand, Category as ShopCategory, Comment as ShopComment, Question as ShopQuestion
from blog.models import Post, Comment as BlogComment


class HomeService:
    """
    Encapsulates business logic related to the home application data retrieval and creation.
    """

    @staticmethod
    def get_home_page_data() -> Dict[str, Any]:
        now = timezone.now()

        stories: QuerySet[Story] = Story.objects.filter(is_active=True)
        sliders: QuerySet[Slider] = Slider.objects.filter(is_active=True)
        banners: QuerySet[Banner] = Banner.objects.filter(is_active=True)
        store_reviews: QuerySet[StoreReview] = StoreReview.objects.filter(is_active=True)[:10]

        categories: QuerySet[ShopCategory] = ShopCategory.objects.filter(is_active=True, parent__isnull=True)[:10]
        brands: QuerySet[Brand] = Brand.objects.filter(is_active=True)[:10]

        product_prefetch: list = [
            'variants__attribute_values',
            'gallery',
            'videos',
            'price_history',
            Prefetch('comments', queryset=ShopComment.objects.filter(is_approved=True), to_attr='approved_comments'),
            Prefetch('questions', queryset=ShopQuestion.objects.filter(is_approved=True), to_attr='approved_questions')
        ]

        special_offers: QuerySet[Product] = Product.objects.filter(
            is_active=True,
            special_discount_percent__gt=0,
            special_offer_end__isnull=False,
            special_offer_end__gt=now
        ).select_related('brand', 'category').prefetch_related(*product_prefetch).order_by('special_offer_end')[:10]

        best_sellers: QuerySet[Product] = Product.objects.filter(
            is_active=True
        ).select_related('brand', 'category').prefetch_related(*product_prefetch).order_by('-sold_count')[:10]

        latest_posts: QuerySet[Post] = Post.objects.filter(is_published=True).select_related('category', 'author').prefetch_related(
            'tags',
            Prefetch('comments', queryset=BlogComment.objects.filter(is_approved=True), to_attr='approved_comments')
        ).order_by('-created_at')[:6]

        return {
            'stories': stories,
            'sliders': sliders,
            'banners': banners,
            'categories': categories,
            'special_offers': special_offers,
            'best_sellers': best_sellers,
            'brands': brands,
            'store_reviews': store_reviews,
            'latest_posts': latest_posts,
        }

    @staticmethod
    def get_site_settings() -> SiteSetting:
        return SiteSetting.load()

    @staticmethod
    def get_faqs() -> QuerySet[FAQ]:
        return FAQ.objects.filter(is_active=True)

    @staticmethod
    def get_about_us() -> Optional[AboutPage]:
        return AboutPage.objects.filter(is_active=True).first()

    @staticmethod
    def create_contact_message(validated_data: Dict[str, Any]) -> ContactMessage:
        return ContactMessage.objects.create(**validated_data)