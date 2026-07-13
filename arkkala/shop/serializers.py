"""
Serializers for the Shop App.
Passes detailed SEO, AEO, and GEO metadata structures to Next.js completely.
"""
from typing import Any, Dict, List, Optional
from rest_framework import serializers
from rest_framework.request import Request
from .models import Brand, Product, ProductVariant, AttributeValue, Comment, ProductGallery, ProductVideo, Question, PriceHistory
from platform_seo.serializers import BaseSeoSerializer


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for the Question model to display approved Q&As (AEO source)."""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['uuid', 'user_name', 'text', 'answer_text', 'created_at']

    def get_user_name(self, obj: Question) -> str:
        """Returns the full name of the user or a guest name."""
        if obj.user and obj.user.get_full_name():
            return obj.user.get_full_name()
        return obj.name or "کاربر مهمان"


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for the Brand model."""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['uuid', 'title', 'slug', 'logo', 'logo_alt', 'product_count']

    def get_product_count(self, obj: Brand) -> int:
        """Return the number of active products for this brand."""
        return obj.products.filter(is_active=True).count()


class ProductSeoSerializer(BaseSeoSerializer):
    """SEO fields Serializer for Product."""
    class Meta:
        model = Product
        fields = [
            'seo_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'schema_markup',
            'og_title', 'og_type', 'og_description', 'og_url', 'og_site_name', 'og_locale',
            'twitter_card', 'twitter_site', 'twitter_creator'
        ]
        
    def get_canonical_url(self, obj: Product) -> str:
        """Override to provide frontend product path."""
        return self.get_frontend_url(f"/product/{obj.slug}/")


class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for Variant Attribute Values."""
    attribute_name = serializers.CharField(source='attribute.title')

    class Meta:
        model = AttributeValue
        fields = ['uuid', 'attribute_name', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for Product Variants."""
    attributes = AttributeValueSerializer(source='attribute_values', many=True)

    class Meta:
        model = ProductVariant
        fields = ['uuid', 'price', 'wholesale_price', 'inventory', 'attributes']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Product Comments."""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['uuid', 'user_name', 'body', 'rating', 'created_at']
        
    def get_user_name(self, obj: Comment) -> str:
        """Get User Full Name or return anonymous string."""
        if obj.user and obj.user.get_full_name():
            return obj.user.get_full_name()
        return "کاربر ناشناس"


class ProductGallerySerializer(serializers.ModelSerializer):
    """Serializer for Product Images Gallery with Alt Tags (SEO)."""
    url = serializers.FileField(source='image')
    
    class Meta:
        model = ProductGallery
        fields = ['url', 'image_alt', 'is_main']


class ProductVideoSerializer(serializers.ModelSerializer):
    """Serializer for Product Videos."""
    url = serializers.FileField(source='video_file')
    
    class Meta:
        model = ProductVideo
        fields = ['uuid', 'title', 'url']


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for historical prices to build the chart."""
    class Meta:
        model = PriceHistory
        fields = ['price', 'created_at']


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Main Product Serializer for detailed view optimized for Prefetched data.
    Sends GEO and AEO explicit data arrays directly to frontend.
    """
    brand = BrandSerializer(read_only=True)
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
            'uuid', 'title', 'english_title', 'slug', 'brand', 'short_description', 'description', 
            'key_takeaways', 'expert_reviewer', 'citations', 
            'base_price', 'base_inventory', 'weight', 'volume',
            'is_wholesale', 'wholesale_min_quantity', 'wholesale_base_price',
            'special_discount_percent', 'special_offer_end', 'is_special_offer',
            'sold_count', 'view_count', 'average_rating',
            'is_variable', 'gallery', 'videos', 'variants', 'comments', 'seo', 'created_at', 
            'questions', 'price_history', 'is_favorite'
        ]

    def get_is_favorite(self, obj: Product) -> bool:
        """Check annotated favorite data to avoid redundant DB queries."""
        if hasattr(obj, 'is_user_favorite'):
            return obj.is_user_favorite
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def get_comments(self, obj: Product) -> List[Dict[str, Any]]:
        """Retrieve approved comments utilizing prefetched data."""
        if hasattr(obj, 'approved_comments'):
            return CommentSerializer(obj.approved_comments, many=True).data
        approved_comments = obj.comments.filter(is_approved=True)
        return CommentSerializer(approved_comments, many=True).data

    def get_questions(self, obj: Product) -> List[Dict[str, Any]]:
        """Retrieve approved questions utilizing prefetched data."""
        if hasattr(obj, 'approved_questions'):
            return QuestionSerializer(obj.approved_questions, many=True, context=self.context).data
        approved_questions = obj.questions.filter(is_approved=True)
        return QuestionSerializer(approved_questions, many=True, context=self.context).data


class UserCommentSerializer(serializers.ModelSerializer):
    """Serializer specifically for the dashboard to show the user's comments alongside product info."""
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    product_image = serializers.SerializerMethodField()
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'product_title', 'product_slug', 'product_image', 'body', 'rating', 'is_approved', 'created_at']

    def get_product_image(self, obj: Comment) -> Optional[str]:
        if obj.product:
            main_img = obj.product.gallery.filter(is_main=True).first()
            if not main_img:
                main_img = obj.product.gallery.first()
            if main_img and main_img.image:
                request: Optional[Request] = self.context.get('request')
                return request.build_absolute_uri(main_img.image.url) if request else main_img.image.url
        return None