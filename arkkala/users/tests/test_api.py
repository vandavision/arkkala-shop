import pytest
from typing import Any, Dict
from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import override_settings

from users.models.otp import OTPRequest

User = get_user_model()

@pytest.mark.django_db
class TestAPIEndpoints:
    @override_settings(AUTH_MODE='OTP')
    def test_api_otp_send_rate_limit_response(self, api_client: APIClient) -> None:
        url: str = reverse('otp_send')
        data: Dict[str, str] = {"phone_number": "09125555555"}
        
        response1 = api_client.post(url, data, format='json')
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = api_client.post(url, data, format='json')
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "قبلاً ارسال شده است" in response2.data['error']

    def test_api_address_queryset_security_leak(self, api_client: APIClient, test_user: Any) -> None:
        other_user = User.objects.create_user(username="09123333333", phone_number="09123333333")
        from users.models.address import UserAddress
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

    def test_api_auth_config_returns_mode(self, api_client: APIClient) -> None:
        url: str = reverse('auth_config')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'mode' in response.data

    def test_api_profile_requires_auth(self, api_client: APIClient) -> None:
        url: str = reverse('profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_api_profile_retrieval(self, api_client: APIClient, test_user: User) -> None:
        api_client.force_authenticate(user=test_user)
        url: str = reverse('profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == test_user.phone_number

    @override_settings(AUTH_MODE='OTP')
    def test_api_otp_verify_success(self, api_client: APIClient, valid_otp_request: OTPRequest) -> None:
        url = reverse('otp_verify')
        data = {"phone_number": valid_otp_request.identifier, "code": valid_otp_request.code}
        res = api_client.post(url, data, format='json')
        assert res.status_code == status.HTTP_200_OK
        assert 'access' in res.data

    @override_settings(AUTH_MODE='EMAIL')
    def test_api_email_register(self, api_client: APIClient) -> None:
        url = reverse('register')
        data = {"email": "api@test.com", "password": "Pass123!", "password_confirm": "Pass123!"}
        res = api_client.post(url, data, format='json')
        assert res.status_code == status.HTTP_201_CREATED

    @override_settings(AUTH_MODE='EMAIL')
    def test_api_email_login(self, api_client: APIClient, test_user: User) -> None:
        test_user.email = "api_login@test.com"
        test_user.save()
        url = reverse('login')
        data = {"email": "api_login@test.com", "password": "EnterprisePass123!"}
        res = api_client.post(url, data, format='json')
        assert res.status_code == status.HTTP_200_OK
        assert 'access' in res.data

    @override_settings(AUTH_MODE='EMAIL')
    @patch('users.application.commands.auth.send_mail')
    def test_api_password_reset_request(self, mock_send: Any, api_client: APIClient, test_user: User) -> None:
        test_user.email = "api_reset@test.com"
        test_user.save()
        url = reverse('password_reset_request')
        data = {"email": "api_reset@test.com"}
        res = api_client.post(url, data, format='json')
        assert res.status_code == status.HTTP_200_OK

    @override_settings(AUTH_MODE='EMAIL')
    def test_api_password_reset_confirm(self, api_client: APIClient, test_user: User) -> None:
        test_user.email = "api_confirm@test.com"
        test_user.save()
        OTPRequest.objects.create(identifier=test_user.email, code="123456", ip_address="127.0.0.1", expires_at=timezone.now() + timedelta(minutes=5))
        url = reverse('password_reset_confirm')
        data = {"email": test_user.email, "code": "123456", "new_password": "NewPass123!", "new_password_confirm": "NewPass123!"}
        res = api_client.post(url, data, format='json')
        assert res.status_code == status.HTTP_200_OK

    def test_api_address_create_and_set_default(self, api_client: APIClient, test_user: User) -> None:
        api_client.force_authenticate(user=test_user)
        url = reverse('user-address-list')
        data = {
            "title": "Work", "recipient_first_name": "A", "recipient_last_name": "B",
            "recipient_phone": "0912", "province": "Teh", "city": "Teh",
            "postal_address": "X", "postal_code": "123", "plaque": "1"
        }
        res = api_client.post(url, data, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        
        uuid_str = res.data['uuid']
        set_default_url = reverse('user-address-set-default', args=[uuid_str])
        res2 = api_client.post(set_default_url)
        assert res2.status_code == status.HTTP_200_OK

    @override_settings(AUTH_MODE='EMAIL')
    def test_api_otp_forbidden_in_email_mode(self, api_client: APIClient) -> None:
        res1 = api_client.post(reverse('otp_send'), {}, format='json')
        res2 = api_client.post(reverse('otp_verify'), {}, format='json')
        assert res1.status_code == status.HTTP_403_FORBIDDEN
        assert res2.status_code == status.HTTP_403_FORBIDDEN

    @override_settings(AUTH_MODE='OTP')
    def test_api_email_forbidden_in_otp_mode(self, api_client: APIClient) -> None:
        res1 = api_client.post(reverse('register'), {}, format='json')
        res2 = api_client.post(reverse('login'), {}, format='json')
        res3 = api_client.post(reverse('password_reset_request'), {}, format='json')
        res4 = api_client.post(reverse('password_reset_confirm'), {}, format='json')
        assert res1.status_code == status.HTTP_403_FORBIDDEN
        assert res2.status_code == status.HTTP_403_FORBIDDEN
        assert res3.status_code == status.HTTP_403_FORBIDDEN
        assert res4.status_code == status.HTTP_403_FORBIDDEN