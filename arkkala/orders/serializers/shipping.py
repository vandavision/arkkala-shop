from rest_framework import serializers
from orders.models import ShippingMethod


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for Shipping Methods."""
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'description', 'base_cost', 'is_pay_on_delivery']