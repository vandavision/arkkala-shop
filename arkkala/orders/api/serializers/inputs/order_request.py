from rest_framework import serializers


class OrderRequestInputSerializer(serializers.Serializer):
    """Input validation for order cancel/return requests."""
    order = serializers.UUIDField()
    request_type = serializers.ChoiceField(choices=['cancel', 'return'])
    reason = serializers.CharField()