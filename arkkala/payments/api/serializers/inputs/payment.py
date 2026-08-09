from rest_framework import serializers

class PaymentRequestInputSerializer(serializers.Serializer):
    """Payload serializer for initiating a payment."""
    order_id = serializers.UUIDField()
    gateway = serializers.CharField(max_length=50, default='zarinpal')