from rest_framework import serializers
from orders.models import CartItem
from orders.services.cart import CartService
from shop.serializers import ProductDetailSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for items within a cart."""
    id = serializers.UUIDField(source='uuid', read_only=True)
    product_details = ProductDetailSerializer(source='product', read_only=True)
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_details', 'variant', 'variant_details', 'quantity', 'unit_price', 'total_price']
        extra_kwargs = {'product': {'write_only': True}, 'variant': {'write_only': True}}
        
    def get_unit_price(self, obj: CartItem):
        return CartService.calculate_item_price(obj)
        
    def get_total_price(self, obj: CartItem):
        return CartService.calculate_item_price(obj) * obj.quantity