"""
Serializers for the Shop App.
Handles data transformation and validation for shop models.
"""
from typing import Any, Dict, List, Optional
from rest_framework import serializers
from rest_framework.request import Request
from .models import Brand, Product, ProductVariant, AttributeValue, Comment, ProductGallery, ProductVideo, Question, PriceHistory


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model to display approved Q&As.
    """
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
        fields = ['uuid', 'title', 'slug', 'logo', 'product_count']

    def get_product_count(self, obj: Brand) -> int:
        """Return the number of active products for this brand."""
        return obj.products.filter(is_active=True).count()


class ProductSeoSerializer(serializers.ModelSerializer):
    """
    Serializer for handling SEO-related fields of the Product model.
    Utilizes platform_seo package features.
    """
    json_ld = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()
    meta_keywords = serializers.JSONField(source='keywords', read_only=True)
    canonical_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['meta_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'json_ld']

    def get_json_ld(self, obj: Product) -> Dict[str, Any]:
        """Get generated JSON-LD from Product model for rich snippets."""
        return obj.generate_json_ld() if hasattr(obj, 'generate_json_ld') else {}

    def get_og_image_url(self, obj: Product) -> Optional[str]:
        """Construct the absolute URL for the OpenGraph image."""
        if hasattr(obj, 'og_image') and obj.og_image:
            request: Optional[Request] = self.context.get('request')
            return request.build_absolute_uri(obj.og_image.url) if request else obj.og_image.url
        return None
        
    def get_canonical_url(self, obj: Product) -> str:
        """
        Construct the canonical URL for the product.
        Uses 'slug' instead of 'id' for better SEO standards.
        """
        request: Optional[Request] = self.context.get('request')
        path: str = f"/product/{obj.slug}/"
        if request:
            return request.build_absolute_uri(path)
        return path


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
    """Serializer for Product Images Gallery."""
    url = serializers.FileField(source='image')
    
    class Meta:
        model = ProductGallery
        fields = ['url', 'is_main']


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
    Main Product Serializer for detailed view.
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
            'base_price', 'base_inventory', 'weight', 'volume',
            'is_wholesale', 'wholesale_min_quantity', 'wholesale_base_price',
            'special_discount_percent', 'special_offer_end', 'is_special_offer',
            'sold_count', 'view_count', 'average_rating',
            'is_variable', 'gallery', 'videos', 'variants', 'comments', 'seo', 'created_at', 
            'questions', 'price_history', 'is_favorite'
        ]

    def get_is_favorite(self, obj: Product) -> bool:
        """Check if current user has favorited this product."""
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def get_comments(self, obj: Product) -> List[Dict[str, Any]]:
        """Retrieve approved comments."""
        approved_comments = obj.comments.filter(is_approved=True)
        return CommentSerializer(approved_comments, many=True).data

    def get_questions(self, obj: Product) -> List[Dict[str, Any]]:
        """Retrieve approved questions."""
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