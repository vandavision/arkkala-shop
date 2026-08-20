from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models.address import UserAddress

User = get_user_model()

class UserProfileOutputSerializer(serializers.ModelSerializer):
    """
    Exposes unified user identity formats accurately.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'first_name', 'last_name', 'avatar', 'created_at', 'date_joined')
        read_only_fields = ('created_at', 'email', 'phone_number', 'id', 'date_joined')

class UserAddressOutputSerializer(serializers.ModelSerializer):
    """
    Translates robust geographical references efficiently.
    """
    class Meta:
        model = UserAddress
        fields = [
            'uuid', 'title', 'recipient_first_name', 'recipient_last_name',
            'recipient_phone', 'province', 'city', 'postal_address',
            'postal_code', 'plaque', 'building_unit', 'is_default', 'created_at'
        ]
        read_only_fields = ['uuid', 'created_at']