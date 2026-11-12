from rest_framework import serializers
from django.db.models import Q
from shop.models import Category, Brand, Product


class SearchProductItemSerializer(serializers.ModelSerializer):
    """Minimal serializer for products inside search and menus."""
    image_url = serializers.SerializerMethodField()
    final_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = ['uuid', 'title', 'slug', 'base_price', 'final_price', 'image_url']

    def get_image_url(self, obj: Product) -> str | None:
        gallery_images = list(obj.gallery.all())
        main_image = next((img for img in gallery_images if img.is_main), None)

        if not main_image and gallery_images:
            main_image = gallery_images[0]

        if main_image and main_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
            return main_image.image.url
        return None


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Recursive serializer to build a category tree (Parent -> Children)."""
    children = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug', 'image', 'children', 'products']

    def get_children(self, obj: Category):
        children = [child for child in obj.children.all() if child.is_active]
        if children:
            return CategoryTreeSerializer(children, many=True, context=self.context).data
        return []

    def get_products(self, obj: Category):
        if obj.parent is None:
            products = Product.objects.filter(
                Q(category=obj) | Q(category__parent=obj),
                is_active=True
            ).prefetch_related('gallery').distinct().order_by('-view_count')[:4]
            return SearchProductItemSerializer(products, many=True, context=self.context).data
        return []


class BrandBrowseSerializer(serializers.ModelSerializer):
    """Serializer for Brands Page including product counts."""
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = ['uuid', 'title', 'slug', 'logo', 'product_count']


class SearchCategoryItemSerializer(serializers.ModelSerializer):
    """Minimal serializer for categories in global search."""
    class Meta:
        model = Category
        fields = ['uuid', 'title', 'slug', 'image']


class SearchBrandItemSerializer(serializers.ModelSerializer):
    """Minimal serializer for brands in global search."""
    class Meta:
        model = Brand
        fields = ['uuid', 'title', 'slug', 'logo']


class GlobalSearchResponseSerializer(serializers.Serializer):
    """Aggregates all store search results into one clean JSON response."""
    products = SearchProductItemSerializer(many=True, read_only=True)
    brands = SearchBrandItemSerializer(many=True, read_only=True)
    categories = SearchCategoryItemSerializer(many=True, read_only=True)