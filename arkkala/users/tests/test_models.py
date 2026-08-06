import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models.otp import OTPRequest
from users.models.address import UserAddress

User = get_user_model()

@pytest.mark.django_db
class TestUserModels:
    def test_user_creation_requires_identifier(self) -> None:
        user = User(username="invalid_user")
        with pytest.raises(ValidationError):
            user.clean()

    def test_user_creation_with_valid_phone(self) -> None:
        user = User(username="09123334455", phone_number="09123334455")
        user.clean()
        user.save()
        assert user.id is not None
        assert str(user) == "09123334455"

    def test_user_manager_no_username(self) -> None:
        with pytest.raises(ValueError) as exc:
            User.objects.create_user(username="")
        assert "الزامی است" in str(exc.value)

    def test_user_manager_create_superuser(self) -> None:
        su = User.objects.create_superuser(username="admin@test.com", email="admin@test.com", password="123")
        assert su.is_superuser is True
        assert su.is_staff is True

    def test_user_clean_empty_strings(self) -> None:
        user = User(username="09121234567", email="", phone_number="")
        with pytest.raises(ValidationError):
            user.clean()

    def test_otp_auto_expiration_assignment(self) -> None:
        otp = OTPRequest(identifier="09121234567", code="12345", ip_address="127.0.0.1")
        otp.clean()
        assert otp.expires_at is not None

    def test_user_address_default_atomicity(self, test_user: User) -> None:
        from users.repositories.address import AddressRepository
        repo = AddressRepository()
        
        addr1 = UserAddress.objects.create(
            user=test_user, title="Home 1", recipient_first_name="A", recipient_last_name="B",
            recipient_phone="09120000000", is_default=False, country="Iran"
        )
        addr2 = UserAddress.objects.create(
            user=test_user, title="Home 2", recipient_first_name="C", recipient_last_name="D",
            recipient_phone="09120000000", is_default=False, country="Iran"
        )
        
        repo.set_default_address(test_user.id, addr1.uuid)
        addr1.refresh_from_db()
        addr2.refresh_from_db()
        
        assert addr1.is_default is True
        assert addr2.is_default is False
        
        repo.set_default_address(test_user.id, addr2.uuid)
        addr1.refresh_from_db()
        addr2.refresh_from_db()
        
        assert addr1.is_default is False
        assert addr2.is_default is True

    def test_address_clean_default_country(self, test_user: User) -> None:
        address = UserAddress(
            user=test_user, title="Home", recipient_first_name="A", recipient_last_name="B",
            recipient_phone="0912000", province="T", city="T", postal_address="X", postal_code="1"
        )
        address.clean()
        assert address.country == "ایران"