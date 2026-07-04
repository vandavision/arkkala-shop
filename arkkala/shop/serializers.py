"""
Serializers for the Shop App.
"""
from typing import Any, Dict, List
from rest_framework import serializers
from .models import Brand, Product, ProductVariant, AttributeValue, Comment, ProductGallery


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand."""
    class Meta:
        model = Brand
        fields = ['id', 'title', 'slug', 'logo']


class ProductSeoSerializer(serializers.ModelSerializer):
    """SEO fields Serializer."""
    json_ld = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['meta_keywords', 'meta_description', 'canonical_url', 'og_image_url', 'json_ld']

    def get_json_ld(self, obj: Product) -> Dict[str, Any]:
        """Get generated JSON-LD from Product model."""
        return obj.generate_json_ld() if hasattr(obj, 'generate_json_ld') else {}

    def get_og_image_url(self, obj: Product) -> str | None:
        """Get OG Image URL."""
        return obj.og_image.url if hasattr(obj, 'og_image') and obj.og_image else None


class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for Variant Attributes."""
    attribute_name = serializers.CharField(source='attribute.title')

    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute_name', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for Product Variants."""
    attributes = AttributeValueSerializer(source='attribute_values', many=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'price', 'wholesale_price', 'inventory', 'attributes']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Product Comments."""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'body', 'rating', 'created_at']
        
    def get_user_name(self, obj: Comment) -> str:
        """Get User Full Name or return anonymous string."""
        return obj.user.get_full_name() if obj.user and obj.user.get_full_name() else "کاربر ناشناس"


class ProductGallerySerializer(serializers.ModelSerializer):
    """Serializer for Product Images."""
    url = serializers.FileField(source='image')
    
    class Meta:
        model = ProductGallery
        fields = ['url', 'is_main']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Main Serializer for Product detail and list."""
    brand = BrandSerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    seo = ProductSeoSerializer(source='*', read_only=True)
    gallery = ProductGallerySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'english_title', 'slug', 'brand', 'short_description', 'description', 
            'base_price', 'base_inventory', 
            'is_wholesale', 'wholesale_min_quantity', 'wholesale_base_price',
            'sold_count', 'view_count', 'average_rating',
            'is_variable', 'gallery', 'variants', 'comments', 'seo', 'created_at'
        ]

    def get_comments(self, obj: Product) -> List[Dict[str, Any]]:
        """Return approved comments for the product."""
        approved_comments = obj.comments.filter(is_approved=True)
        return CommentSerializer(approved_comments, many=True).data