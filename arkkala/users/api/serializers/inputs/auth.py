from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class EmailRegisterInputSerializer(serializers.Serializer):
    """
    Performs precise validation parsing input parameters correctly avoiding business logic dynamically.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "رمز عبور و تکرار آن مطابقت ندارند."})
        return attrs

class EmailLoginInputSerializer(serializers.Serializer):
    """
    Verifies payload structures purely ensuring security compliance perfectly.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

class PasswordResetRequestInputSerializer(serializers.Serializer):
    """
    Validates identity markers initiating complex flows cleanly.
    """
    email = serializers.EmailField(required=True)

class PasswordResetConfirmInputSerializer(serializers.Serializer):
    """
    Ensures safe transmission establishing valid recovery payload configurations definitively.
    """
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "رمز عبور و تکرار آن مطابقت ندارند."})
        return attrs

class OTPSendInputSerializer(serializers.Serializer):
    """
    Filters structural data generating required boundaries inherently.
    """
    phone_number = serializers.CharField(max_length=15, required=True)

class OTPVerifyInputSerializer(serializers.Serializer):
    """
    Confirms payload structures successfully mapping structural verifications completely.
    """
    phone_number = serializers.CharField(max_length=15, required=True)
    code = serializers.CharField(max_length=6, required=True)