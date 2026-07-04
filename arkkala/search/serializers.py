"""
Serializers for the Search App APIs.
"""
from rest_framework import serializers
from shop.models import Category, Brand, Product
from blog.models import Post



class CategoryTreeSerializer(serializers.ModelSerializer):
    """Recursive serializer to build a category tree (Parent -> Children)."""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'children']

    def get_children(self, obj: Category):
        if obj.children.exists():
            active_children = obj.children.filter(is_active=True)
            return CategoryTreeSerializer(active_children, many=True).data
        return []


class BrandBrowseSerializer(serializers.ModelSerializer):
    """Serializer for Brands Page including product counts."""
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'title', 'slug', 'logo', 'product_count']



class SearchProductItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'base_price', 'image_url']
        
    def get_image_url(self, obj: Product) -> str | None:
        main_image = obj.gallery.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        first_image = obj.gallery.first()
        return first_image.image.url if first_image else None


class SearchPostItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'image']


class SearchCategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class SearchBrandItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'title', 'slug', 'logo']


class GlobalSearchResponseSerializer(serializers.Serializer):
    """Aggregates all search results into one clean JSON response."""
    products = SearchProductItemSerializer(many=True, read_only=True)
    posts = SearchPostItemSerializer(many=True, read_only=True)
    brands = SearchBrandItemSerializer(many=True, read_only=True)
    categories = SearchCategoryItemSerializer(many=True, read_only=True)