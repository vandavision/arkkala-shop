import pytest
from django.contrib.auth import get_user_model
from users.serializers.auth import (
    EmailRegisterSerializer,
    PasswordResetConfirmSerializer,
    EmailLoginSerializer
)

User = get_user_model()

@pytest.mark.django_db
class TestSerializers:
    def test_email_register_password_mismatch(self) -> None:
        data = {
            "email": "test@domain.com",
            "password": "SecurePassword123!",
            "password_confirm": "DifferentPassword123!"
        }
        serializer = EmailRegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors

    def test_password_reset_confirm_mismatch(self) -> None:
        data = {
            "email": "test@domain.com",
            "code": "123456",
            "new_password": "SecurePassword123!",
            "new_password_confirm": "DifferentPassword123!"
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        assert serializer.is_valid() is False
        assert "new_password" in serializer.errors

    def test_email_login_serializer_success(self, test_user: User) -> None:
        test_user.email = "login_ser@test.com"
        test_user.save()
        data = {"email": "login_ser@test.com", "password": "EnterprisePass123!"}
        serializer = EmailLoginSerializer(data=data)
        assert serializer.is_valid() is True
        assert 'access' in serializer.validated_data

    def test_email_login_serializer_invalid(self, test_user: User) -> None:
        test_user.email = "login_ser_fail@test.com"
        test_user.save()
        data = {"email": "login_ser_fail@test.com", "password": "WrongPassword!"}
        serializer = EmailLoginSerializer(data=data)
        assert serializer.is_valid() is False