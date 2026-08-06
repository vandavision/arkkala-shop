from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class EmailRegisterSerializer(serializers.Serializer):
    """
    Schema validation for Email-based registration requests.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates password matching strictly.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "رمز عبور و تکرار آن مطابقت ندارند."})
        return attrs

class EmailLoginSerializer(TokenObtainPairSerializer):
    """
    JWT generation override tailored specifically for exact Email matching.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes JWT override safely.
        """
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField(required=True)
        if self.username_field in self.fields:
            del self.fields[self.username_field]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates payload manually.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = self.get_token(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        raise serializers.ValidationError('ایمیل یا رمز عبور اشتباه است.')

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Schema validation for requesting a password reset email.
    """
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Schema validation for finalizing a new password with an OTP code.
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates password rules properly.
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "رمز عبور و تکرار آن مطابقت ندارند."})
        return attrs

class OTPSendSerializer(serializers.Serializer):
    """
    Schema validation for submitting mobile numbers for OTP.
    """
    phone_number = serializers.CharField(max_length=15, required=True)

class OTPVerifySerializer(serializers.Serializer):
    """
    Schema validation for submitting mobile numbers with verification codes.
    """
    phone_number = serializers.CharField(max_length=15, required=True)
    code = serializers.CharField(max_length=6, required=True)