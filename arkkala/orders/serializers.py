"""
Serializers for Orders App.
"""
from rest_framework import serializers
from .models import CartItem, Order, OrderItem, ShippingMethod, Coupon
from shop.serializers import ProductDetailSerializer, ProductVariantSerializer


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for Shipping Methods."""
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'base_cost', 'is_pay_on_delivery']


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
        extra_kwargs = {
            'product': {'write_only': True},
            'variant': {'write_only': True}
        }
        
    def get_unit_price(self, obj: CartItem):
        from .services import CartService
        return CartService.calculate_item_price(obj)
        
    def get_total_price(self, obj: CartItem):
        from .services import CartService
        return CartService.calculate_item_price(obj) * obj.quantity


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for finalized Order Items."""
    id = serializers.UUIDField(source='uuid', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_title', 'quantity', 'unit_price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for displaying Orders."""
    id = serializers.UUIDField(source='uuid', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_method_name = serializers.CharField(source='shipping_method.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'shipping_method_name', 'total_items_amount', 
            'discount_amount', 'shipping_cost', 'payable_amount', 'tracking_code', 
            'is_paid', 'created_at', 'items', 'title', 'country', 'province', 'city', 'postal_address', 'postal_code'
        ]


class CheckoutSerializer(serializers.Serializer):
    """Payload serializer for creating an order checkout."""
    shipping_method_id = serializers.UUIDField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    
    guest_first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    guest_last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    guest_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    title = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    province = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    postal_address = serializers.CharField()
    postal_code = serializers.CharField(max_length=20)
    plaque = serializers.CharField(max_length=20)
    building_unit = serializers.CharField(max_length=20, required=False, allow_blank=True)