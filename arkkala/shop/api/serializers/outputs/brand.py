from rest_framework import serializers
from shop.models.brand import Brand

class BrandSerializer(serializers.ModelSerializer):
    """Outputs Brand details."""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['uuid', 'title', 'slug', 'logo', 'logo_alt', 'product_count']

    def get_product_count(self, obj: Brand) -> int:
        return obj.products.filter(is_active=True).count()