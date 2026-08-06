import pytest
from typing import Any
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import override_settings

from users.models.otp import OTPRequest
from users.models.address import UserAddress
from users.application.commands.auth import AuthCommandService
from users.application.commands.profile import ProfileCommandService
from users.application.queries.user import UserQueryService
from users.application.dtos import OTPSendDTO, EmailRegisterDTO, OTPVerifyDTO, PasswordResetConfirmDTO

User = get_user_model()

@pytest.mark.django_db
class TestApplicationServices:
    @override_settings(AUTH_MODE='OTP')
    def test_otp_rate_limiting_anti_spam(self) -> None:
        dto = OTPSendDTO(identifier="09123456789", ip_address="127.0.0.1")
        AuthCommandService.send_otp(dto)

        with pytest.raises(ValueError) as exc:
            AuthCommandService.send_otp(dto)
        
        assert "قبلاً ارسال شده" in str(exc.value)

    @override_settings(AUTH_MODE='OTP')
    def test_otp_max_daily_requests_enforcement(self) -> None:
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
        User.objects.create_user(username="test@arkkala.com", email="test@arkkala.com", password="SecurePassword123!")
        dto = EmailRegisterDTO(email="test@arkkala.com", password="NewPassword123!")
        
        with pytest.raises(ValueError) as exc:
            AuthCommandService.register_email(dto)
            
        assert "قبلاً ثبت شده است" in str(exc.value)

    def test_address_query_isolation(self, test_user: User) -> None:
        other_user = User.objects.create_user(username="09122222222", phone_number="09122222222")
        UserAddress.objects.create(
            user=other_user, title="Office", recipient_first_name="A",
            recipient_last_name="B", recipient_phone="09122222222", country="Iran"
        )
        
        addresses = UserQueryService.get_user_addresses(test_user)
        assert addresses.count() == 0

    def test_verify_otp_and_login_success(self, valid_otp_request: OTPRequest) -> None:
        dto = OTPVerifyDTO(identifier=valid_otp_request.identifier, code=valid_otp_request.code)
        result = AuthCommandService.verify_otp_and_login(dto)
        
        assert 'access' in result
        assert 'refresh' in result
        assert result['is_new_user'] is True

    @patch('users.services.sms.KavenegarService.send_otp')
    def test_kavenegar_sms_integration_failure(self, mock_send_otp: Any) -> None:
        mock_send_otp.return_value = False
        dto = OTPSendDTO(identifier="09125555555", ip_address="127.0.0.1")
        
        with pytest.raises(ValueError) as exc:
            AuthCommandService.send_otp(dto)
            
        assert "خطا در ارتباط با سرویس پیامکی" in str(exc.value)
        assert OTPRequest.objects.filter(identifier="09125555555").count() == 0

    @patch('users.application.commands.auth.send_mail')
    def test_send_otp_email_success(self, mock_send_mail: Any) -> None:
        dto = OTPSendDTO(identifier="test@arkkala.com", ip_address="127.0.0.1", is_email_reset=True)
        AuthCommandService.send_otp(dto)
        assert mock_send_mail.called

    @patch('users.application.commands.auth.send_mail', side_effect=Exception("SMTP error"))
    def test_send_otp_email_failure(self, mock_send_mail: Any) -> None:
        dto = OTPSendDTO(identifier="test@arkkala.com", ip_address="127.0.0.1", is_email_reset=True)
        with pytest.raises(ValueError) as exc:
            AuthCommandService.send_otp(dto)
        assert "خطا در ارسال ایمیل" in str(exc.value)

    def test_register_email_success(self) -> None:
        dto = EmailRegisterDTO(email="new@arkkala.com", password="Pass123!")
        user = AuthCommandService.register_email(dto)
        assert user.email == "new@arkkala.com"
        assert user.check_password("Pass123!")

    def test_reset_password_success(self, test_user: User) -> None:
        test_user.email = "test@arkkala.com"
        test_user.save()
        OTPRequest.objects.create(identifier="test@arkkala.com", code="123456", ip_address="127.0.0.1", expires_at=timezone.now() + timedelta(minutes=5))
        dto = PasswordResetConfirmDTO(email="test@arkkala.com", code="123456", new_password="NewPass123!")
        AuthCommandService.verify_reset_code_and_set_password(dto)
        test_user.refresh_from_db()
        assert test_user.check_password("NewPass123!")

    def test_reset_password_invalid_code(self) -> None:
        dto = PasswordResetConfirmDTO(email="test@arkkala.com", code="000000", new_password="NewPass123!")
        with pytest.raises(ValueError):
            AuthCommandService.verify_reset_code_and_set_password(dto)

    def test_reset_password_invalid_user(self) -> None:
        OTPRequest.objects.create(identifier="notfound@arkkala.com", code="123456", ip_address="127.0.0.1", expires_at=timezone.now() + timedelta(minutes=5))
        dto = PasswordResetConfirmDTO(email="notfound@arkkala.com", code="123456", new_password="NewPass123!")
        with pytest.raises(ValueError):
            AuthCommandService.verify_reset_code_and_set_password(dto)

    def test_profile_command_service_set_default(self, test_user: User, test_address: UserAddress) -> None:
        ProfileCommandService.set_default_address(test_user.id, test_address.uuid)
        test_address.refresh_from_db()
        assert test_address.is_default is True

    @override_settings(KAVENEGAR_API_KEY="test_key")
    @patch('requests.post')
    def test_kavenegar_service_http_success(self, mock_post: Any) -> None:
        mock_post.return_value.status_code = 200
        from users.services.sms import KavenegarService
        assert KavenegarService.send_otp("09121234567", "12345") is True

    @override_settings(KAVENEGAR_API_KEY="test_key")
    @patch('requests.post')
    def test_kavenegar_service_http_error(self, mock_post: Any) -> None:
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Error"
        from users.services.sms import KavenegarService
        assert KavenegarService.send_otp("09121234567", "12345") is False