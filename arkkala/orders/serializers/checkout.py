from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    """Payload serializer for creating an order checkout."""
    shipping_method_id = serializers.UUIDField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    
    guest_first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    guest_last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    guest_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    guest_email = serializers.EmailField(required=False, allow_blank=True)
    guest_password = serializers.CharField(required=False, allow_blank=True)
    
    title = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    province = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    postal_address = serializers.CharField()
    postal_code = serializers.CharField(max_length=20)
    plaque = serializers.CharField(max_length=20)
    building_unit = serializers.CharField(max_length=20, required=False, allow_blank=True)