"""
Serializers for the Search App APIs.
"""
from rest_framework import serializers
from django.db.models import Q
from shop.models import Category, Brand, Product
from shop.serializers import ProductDetailSerializer


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Recursive serializer to build a category tree (Parent -> Children)."""
    children = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug', 'image', 'children', 'products']

    def get_children(self, obj: Category):
        if obj.children.exists():
            active_children = obj.children.filter(is_active=True)
            return CategoryTreeSerializer(active_children, many=True, context=self.context).data
        return []

    def get_products(self, obj: Category):
        if obj.parent is None:
            products = Product.objects.filter(
                Q(category=obj) | Q(category__parent=obj),
                is_active=True
            ).distinct().order_by('-view_count')[:4]
            return ProductDetailSerializer(products, many=True, context=self.context).data
        return []

class BrandBrowseSerializer(serializers.ModelSerializer):
    """Serializer for Brands Page including product counts."""
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = ['uuid', 'title', 'slug', 'logo', 'product_count']

class SearchProductItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['uuid', 'title', 'slug', 'base_price', 'image_url']
        
    def get_image_url(self, obj: Product) -> str | None:
        main_image = obj.gallery.filter(is_main=True).first()
        if not main_image:
            main_image = obj.gallery.first()
            
        if main_image and main_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
            return main_image.image.url
        return None

class SearchCategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug', 'image', 'children']

class SearchBrandItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['uuid', 'title', 'slug', 'logo']

class GlobalSearchResponseSerializer(serializers.Serializer):
    """Aggregates all store search results into one clean JSON response."""
    products = SearchProductItemSerializer(many=True, read_only=True)
    brands = SearchBrandItemSerializer(many=True, read_only=True)
    categories = SearchCategoryItemSerializer(many=True, read_only=True)