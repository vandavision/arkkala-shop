from typing import Any, Dict, List
from rest_framework import serializers
from platform_seo.serializers import BaseSeoSerializer
from shop.models.product import Product, ProductGallery, ProductVideo, PriceHistory, ProductVariant
from shop.models.category import Category
from .brand import BrandSerializer
from .attribute import AttributeValueSerializer
from .interaction import CommentSerializer, QuestionSerializer


class ProductCategorySerializer(serializers.ModelSerializer):
    """Outputs basic category details."""
    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug']


class ProductSeoSerializer(BaseSeoSerializer):
    """Outputs SEO bindings."""
    class Meta:
        model = Product
        fields = [
            'seo_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'schema_markup',
            'og_title', 'og_type', 'og_description', 'og_url', 'og_site_name', 'og_locale',
            'twitter_card', 'twitter_site', 'twitter_creator'
        ]
        
    def get_canonical_url(self, obj: Product) -> str:
        return self.get_frontend_url(f"/product/{obj.slug}/")


class ProductVariantSerializer(serializers.ModelSerializer):
    """Outputs variants natively."""
    attributes = AttributeValueSerializer(source='attribute_values', many=True)
    gallery_image_id = serializers.UUIDField(source='gallery_image.uuid', read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['uuid', 'price', 'wholesale_price', 'inventory', 'gallery_image_id', 'attributes']


class ProductGallerySerializer(serializers.ModelSerializer):
    """Outputs product images."""
    url = serializers.FileField(source='image')
    
    class Meta:
        model = ProductGallery
        fields = ['uuid', 'url', 'image_alt', 'is_main']


class ProductVideoSerializer(serializers.ModelSerializer):
    """Outputs product videos."""
    url = serializers.FileField(source='video_file')
    
    class Meta:
        model = ProductVideo
        fields = ['uuid', 'title', 'url']


class PriceHistorySerializer(serializers.ModelSerializer):
    """Outputs aggregated history."""
    class Meta:
        model = PriceHistory
        fields = ['price', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Outputs complete product entity combining sub-entities."""
    brand = BrandSerializer(read_only=True)
    category = ProductCategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    seo = ProductSeoSerializer(source='*', read_only=True)
    gallery = ProductGallerySerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    questions = serializers.SerializerMethodField()
    price_history = PriceHistorySerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()
    is_special_offer = serializers.BooleanField(source='is_special_offer_active', read_only=True)

    class Meta:
        model = Product
        fields = [
            'uuid', 'title', 'english_title', 'slug', 'category', 'brand', 'short_description', 'description', 
            'key_takeaways', 'expert_reviewer', 'citations', 'base_price', 'base_inventory', 'weight', 'volume',
            'is_wholesale', 'wholesale_min_quantity', 'wholesale_base_price',
            'special_discount_percent', 'special_offer_end', 'is_special_offer',
            'sold_count', 'view_count', 'average_rating', 'is_variable', 'gallery', 'videos', 
            'variants', 'comments', 'seo', 'created_at', 'questions', 'price_history', 'is_favorite'
        ]

    def get_is_favorite(self, obj: Product) -> bool:
        if hasattr(obj, 'is_user_favorite'):
            return obj.is_user_favorite
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def get_comments(self, obj: Product) -> List[Dict[str, Any]]:
        comments = getattr(obj, 'approved_comments', obj.comments.filter(is_approved=True))
        return CommentSerializer(comments, many=True).data

    def get_questions(self, obj: Product) -> List[Dict[str, Any]]:
        questions = getattr(obj, 'approved_questions', obj.questions.filter(is_approved=True))
        return QuestionSerializer(questions, many=True, context=self.context).data