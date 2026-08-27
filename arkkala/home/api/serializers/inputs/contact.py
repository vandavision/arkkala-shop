from rest_framework import serializers

class ContactMessageInputSerializer(serializers.Serializer):
    """
    Input serializer for receiving contact messages.
    """
    full_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=255, required=False, allow_null=True, allow_blank=True)
    subject = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    message = serializers.CharField()