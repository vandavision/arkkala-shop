import pytest
from typing import Any
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models.address import UserAddress
from users.models.otp import OTPRequest
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@pytest.fixture
def api_client() -> APIClient:
    """
    Returns an API client instance securely prepared exclusively for test endpoints.
    """
    return APIClient()

@pytest.fixture
def test_user() -> Any:
    """
    Injects valid user configurations dynamically required heavily across validations.
    """
    user = User(username="09120000000", phone_number="09120000000")
    user.set_password("EnterprisePass123!")
    user.full_clean()
    user.save()
    return user

@pytest.fixture
def test_address(test_user: Any) -> UserAddress:
    """
    Provides a default address for the test user.
    """
    address = UserAddress(
        user=test_user,
        title="Home",
        recipient_first_name="Test",
        recipient_last_name="User",
        recipient_phone="09120000000",
        province="Tehran",
        city="Tehran",
        postal_address="123 Test St.",
        postal_code="1234567890",
        plaque="1",
        country="Iran",
        is_default=False
    )
    address.full_clean()
    address.save()
    return address

@pytest.fixture
def valid_otp_request() -> OTPRequest:
    """
    Provides a valid, unexpired OTP request for verification testing.
    """
    otp = OTPRequest(
        identifier="09121111111",
        code="123456",
        ip_address="127.0.0.1",
        expires_at=timezone.now() + timedelta(minutes=5)
    )
    otp.full_clean()
    otp.save()
    return otp