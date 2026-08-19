from rest_framework import serializers

class TokenOutputSerializer(serializers.Serializer):
    """
    Constructs normalized application response models strictly separating core data dynamically.
    """
    access = serializers.CharField(source='access_token', read_only=True)
    refresh = serializers.CharField(source='refresh_token', read_only=True)
    is_new_user = serializers.BooleanField(read_only=True)