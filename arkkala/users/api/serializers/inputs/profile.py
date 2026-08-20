from typing import Dict, Any, Optional
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models.address import UserAddress

User = get_user_model()

class UserProfileInputSerializer(serializers.ModelSerializer):
    """
    Serializes and validates input data for user profile updates safely.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'avatar']

    def validate_email(self, value: str) -> Optional[str]:
        """
        Converts empty string to None to prevent database unique constraint errors.
        """
        if value == "":
            return None
        return value

    def validate_phone_number(self, value: str) -> Optional[str]:
        """
        Converts empty string to None to maintain data integrity correctly.
        """
        if value == "":
            return None
        return value
        
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures at least one contact method remains available functionally.
        """
        email = attrs.get('email', getattr(self.instance, 'email', None))
        phone = attrs.get('phone_number', getattr(self.instance, 'phone_number', None))
        if not email and not phone:
            raise serializers.ValidationError("وارد کردن حداقل یکی از موارد ایمیل یا شماره تماس الزامی است.")
        return attrs

class UserAddressInputSerializer(serializers.ModelSerializer):
    """
    Ensures safe state translations generating appropriate context strictly securely.
    """
    class Meta:
        model = UserAddress
        fields = [
            'title', 'recipient_first_name', 'recipient_last_name',
            'recipient_phone', 'province', 'city', 'postal_address',
            'postal_code', 'plaque', 'building_unit'
        ]