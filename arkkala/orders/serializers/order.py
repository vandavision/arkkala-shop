from typing import Optional
from rest_framework import serializers
from rest_framework.request import Request
from orders.models import Order, OrderItem, OrderRequest


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for finalized Order Items."""
    id = serializers.UUIDField(source='uuid', read_only=True)
    product_title = serializers.CharField(source='product.title', read_only=True, default='')
    product_slug = serializers.CharField(source='product.slug', read_only=True, default='')
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_title', 'product_slug', 'product_image', 'quantity', 'unit_price', 'total_price']

    def get_product_image(self, obj: OrderItem) -> Optional[str]:
        """Fetch the main image of the ordered product."""
        if obj.product:
            main_img = obj.product.gallery.filter(is_main=True).first() or obj.product.gallery.first()
            if main_img and main_img.image:
                request: Optional[Request] = self.context.get('request')
                return request.build_absolute_uri(main_img.image.url) if request else main_img.image.url
        return None


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for displaying Orders."""
    id = serializers.UUIDField(source='uuid', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_method_name = serializers.CharField(source='shipping_method.name', read_only=True, default='')
    
    customer_first_name = serializers.SerializerMethodField()
    customer_last_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'shipping_method_name', 'total_items_amount', 
            'discount_amount', 'shipping_cost', 'payable_amount', 'tracking_code', 
            'is_paid', 'created_at', 'items', 'title', 'country', 'province', 'city', 
            'postal_address', 'postal_code', 'plaque', 'building_unit',
            'customer_first_name', 'customer_last_name', 'customer_phone'
        ]

    def get_customer_first_name(self, obj: Order) -> str:
        """Resolve first name falling back to guest info if user is absent."""
        if obj.user and obj.user.first_name:
            return obj.user.first_name
        return obj.guest_first_name or ""

    def get_customer_last_name(self, obj: Order) -> str:
        """Resolve last name falling back to guest info if user is absent."""
        if obj.user and obj.user.last_name:
            return obj.user.last_name
        return obj.guest_last_name or ""

    def get_customer_phone(self, obj: Order) -> str:
        """Resolve phone number falling back to guest info if user is absent."""
        if obj.user and obj.user.phone_number:
            return obj.user.phone_number
        return obj.guest_phone or ""


class OrderRequestSerializer(serializers.ModelSerializer):
    """Serializer for order cancellation and returns."""
    id = serializers.UUIDField(source='uuid', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    
    class Meta:
        model = OrderRequest
        fields = [
            'id', 
            'order', 
            'request_type', 
            'request_type_display', 
            'reason', 
            'status', 
            'status_display', 
            'admin_note', 
            'created_at'
        ]
        read_only_fields = ['status', 'admin_note', 'created_at']