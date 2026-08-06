from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models.address import UserAddress

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Data representation rules for profile responses.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'first_name', 'last_name', 'avatar', 'date_joined')
        read_only_fields = ('date_joined', 'email', 'phone_number')

class UserAddressSerializer(serializers.ModelSerializer):
    """
    Data representation rules for Address views.
    """
    class Meta:
        model = UserAddress
        fields = [
            'uuid', 'title', 'recipient_first_name', 'recipient_last_name',
            'recipient_phone', 'province', 'city', 'postal_address',
            'postal_code', 'plaque', 'building_unit', 'is_default', 'created_at'
        ]
        read_only_fields = ['uuid', 'created_at']