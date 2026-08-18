from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class EmailRegisterSerializer(serializers.Serializer):
    """
    Validates structural constraints strictly corresponding to authentication schemas.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "رمز عبور و تکرار آن مطابقت ندارند."})
        return attrs

class EmailLoginSerializer(serializers.Serializer):
    """
    Schema validation for standard Email login requests.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Evaluates reset initiation parameters efficiently.
    """
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Ensures complete conformity over reset confirmations preventing tampering.
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "رمز عبور و تکرار آن مطابقت ندارند."})
        return attrs

class OTPSendSerializer(serializers.Serializer):
    """
    Data check for mobile OTP transmissions.
    """
    phone_number = serializers.CharField(max_length=15, required=True)

class OTPVerifySerializer(serializers.Serializer):
    """
    Data check mapping constraints for SMS OTP matching routines.
    """
    phone_number = serializers.CharField(max_length=15, required=True)
    code = serializers.CharField(max_length=6, required=True)