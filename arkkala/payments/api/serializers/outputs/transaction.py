from rest_framework import serializers
from payments.models.transaction import Transaction

class TransactionOutputSerializer(serializers.ModelSerializer):
    """Serializer for outputting transaction history."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'order', 'amount', 'status', 'status_display', 'gateway', 'ref_id', 'created_at']