import pytest
from typing import Any, Dict
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import override_settings

from users.models.otp import OTPRequest
from users.models.address import UserAddress
from users.application.commands.auth import AuthCommandService
from users.application.dtos import OTPSendDTO, EmailRegisterDTO
from users.application.queries.user import UserQueryService

User = get_user_model()

@pytest.mark.django_db
class TestUserEnterpriseArchitecture:
    """
    Enterprise-grade test suite covering validations, security safely testing strict boundaries.
    """

    def test_user_model_strict_validation(self) -> None:
        """
        Ensures strict user constraints logic blocks creation cleanly missing email/phone properly.
        """
        user = User(username="invalid_user")
        with pytest.raises(ValidationError):
            user.clean()

    @override_settings(AUTH_MODE='OTP')
    def test_otp_rate_limiting_anti_spam(self) -> None:
        """
        Triggers explicit verification safely against spam limiting bounds accurately.
        """
        dto = OTPSendDTO(identifier="09123456789", ip_address="127.0.0.1")
        AuthCommandService.send_otp(dto)

        with pytest.raises(ValueError) as exc:
            AuthCommandService.send_otp(dto)
        
        assert "قبلاً ارسال شده" in str(exc.value)

    @override_settings(AUTH_MODE='OTP')
    def test_otp_max_daily_requests_enforcement(self) -> None:
        """
        Prevents DDOS correctly enforcing hard block configurations flawlessly.
        """
        now = timezone.now()
        for i in range(5):
            OTPRequest.objects.create(
                identifier="09129999999",
                code=str(10000 + i),
                ip_address="127.0.0.1",
                created_at=now - timedelta(hours=1),
                expires_at=now + timedelta(minutes=2)
            )

        dto = OTPSendDTO(identifier="09129999999", ip_address="127.0.0.1")
        with pytest.raises(ValueError) as exc:
            AuthCommandService.send_otp(dto)
            
        assert "بیش از حد مجاز" in str(exc.value)

    @override_settings(AUTH_MODE='EMAIL')
    def test_email_registration_duplicate_prevention(self) -> None:
        """
        Triggers clean duplicate handler logically correctly intercepting prior saving states seamlessly.
        """
        User.objects.create_user(username="test@arkkala.com", email="test@arkkala.com", password="SecurePassword123!")
        dto = EmailRegisterDTO(email="test@arkkala.com", password="NewPassword123!")
        
        with pytest.raises(ValueError) as exc:
            AuthCommandService.register_email(dto)
            
        assert "قبلاً ثبت شده است" in str(exc.value)

    def test_address_repository_and_query_isolation(self) -> None:
        """
        Performs data integrity verification executing logically against strictly locked scopes safely.
        """
        user1 = User.objects.create_user(username="09121111111", phone_number="09121111111")
        user2 = User.objects.create_user(username="09122222222", phone_number="09122222222")

        UserAddress.objects.create(
            user=user1,
            title="Home 1",
            recipient_first_name="A",
            recipient_last_name="B",
            recipient_phone="09121111111",
            country="Iran"
        )
        
        UserAddress.objects.create(
            user=user2,
            title="Home 2",
            recipient_first_name="C",
            recipient_last_name="D",
            recipient_phone="09122222222",
            country="Iran"
        )

        user1_addresses = UserQueryService.get_user_addresses(user1)
        assert user1_addresses.count() == 1
        assert user1_addresses.first().user == user1

    def test_api_address_queryset_security_leak(self, api_client: APIClient, test_user: Any) -> None:
        """
        Eliminates vulnerability ensuring endpoint outputs isolated arrays dynamically securely configured.
        """
        other_user = User.objects.create_user(username="09123333333", phone_number="09123333333")

        UserAddress.objects.create(
            user=other_user,
            title="Office",
            recipient_first_name="John",
            recipient_last_name="Doe",
            recipient_phone="09123333333",
            country="Iran"
        )

        api_client.force_authenticate(user=test_user)
        url: str = reverse('user-address-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    @override_settings(AUTH_MODE='OTP')
    def test_api_otp_send_rate_limit_response(self, api_client: APIClient) -> None:
        """
        Checks payload accurately throwing accurate bounds constraints responses flawlessly mapped via UI.
        """
        url: str = reverse('otp_send')
        data: Dict[str, str] = {"phone_number": "09125555555"}
        
        response1 = api_client.post(url, data, format='json')
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = api_client.post(url, data, format='json')
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "قبلاً ارسال شده است" in response2.data['error']