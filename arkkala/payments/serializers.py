"""
Serializers for Payments app.
"""
from rest_framework import serializers
from .models import Transaction


class PaymentRequestSerializer(serializers.Serializer):
    """Payload serializer for initiating a payment."""
    order_id = serializers.UUIDField()
    gateway = serializers.CharField(max_length=50, default='zarinpal')


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for outputting transaction history."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'order', 'amount', 'status', 'status_display', 'gateway', 'ref_id', 'created_at']