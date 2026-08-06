import pytest
from typing import Any
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from users.repositories.user import UserRepository
from users.repositories.otp import OTPRepository
from users.repositories.address import AddressRepository
from users.models.otp import OTPRequest
from users.models.address import UserAddress

User = get_user_model()

@pytest.mark.django_db
class TestRepositories:
    """
    Tests for Database Abstraction Layer components.
    """

    def setup_method(self) -> None:
        """
        Initializes repositories for test cases.
        """
        self.user_repo = UserRepository()
        self.otp_repo = OTPRepository()
        self.address_repo = AddressRepository()

    def test_user_repo_get_by_email(self) -> None:
        """
        Verifies retrieval of user strictly by email.
        """
        User.objects.create_user(username="test@test.com", email="test@test.com")
        user = self.user_repo.get_by_email("test@test.com")
        assert user is not None
        assert user.email == "test@test.com"

    def test_user_repo_get_or_create_by_phone(self) -> None:
        """
        Verifies atomic get or create logic for phone identifiers.
        """
        user, created = self.user_repo.get_or_create_by_phone("09129998877")
        assert created is True
        assert user.phone_number == "09129998877"
        
        user2, created2 = self.user_repo.get_or_create_by_phone("09129998877")
        assert created2 is False
        assert user.id == user2.id

    def test_otp_repo_get_valid_otp(self, valid_otp_request: OTPRequest) -> None:
        """
        Ensures OTP retrieval strictly respects expiration and usage status.
        """
        otp = self.otp_repo.get_valid_otp("09121111111", "123456")
        assert otp is not None
        
        otp.is_used = True
        otp.save()
        
        invalid_otp = self.otp_repo.get_valid_otp("09121111111", "123456")
        assert invalid_otp is None

    def test_address_repo_set_default(self, test_user: User, test_address: UserAddress) -> None:
        """
        Tests transaction-safe default address swapping.
        """
        addr2 = UserAddress.objects.create(
            user=test_user, title="Office", recipient_first_name="A", recipient_last_name="B",
            recipient_phone="09120000000", is_default=True
        )
        
        self.address_repo.set_default_address(test_user.id, test_address.uuid)
        
        test_address.refresh_from_db()
        addr2.refresh_from_db()
        
        assert test_address.is_default is True
        assert addr2.is_default is False