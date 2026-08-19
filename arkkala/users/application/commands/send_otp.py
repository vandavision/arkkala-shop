import random
from django.utils import timezone
from datetime import timedelta
from users.application.dto.commands import OTPSendDTO
from users.application.ports.repositories import OTPRepositoryPort
from users.application.ports.notifications import SMSProviderPort, EmailProviderPort
from users.domain.exceptions import RateLimitExceededException, WaitTimeException, ValidationException
from users.domain.events import DomainEventPublisher
from users.models.otp import OTPRequest

class SendOTPCommand:
    """
    Use case managing constraints, creations, and broadcasting routines for access codes.
    """
    def __init__(self, otp_repo: OTPRepositoryPort, sms_provider: SMSProviderPort, email_provider: EmailProviderPort, wait_minutes: int = 2, max_daily: int = 5) -> None:
        self.otp_repo = otp_repo
        self.sms_provider = sms_provider
        self.email_provider = email_provider
        self.wait_minutes = wait_minutes
        self.max_daily = max_daily

    def execute(self, dto: OTPSendDTO) -> None:
        """
        Executes business operations triggering appropriate distribution mechanisms purely.
        """
        now = timezone.now()
        daily_count = self.otp_repo.count_requests_since(dto.identifier, now - timedelta(hours=24))
        if daily_count >= self.max_daily:
            raise RateLimitExceededException("شما بیش از حد مجاز درخواست داده‌اید. لطفاً ۲۴ ساعت دیگر تلاش کنید.")

        last_request = self.otp_repo.get_latest_request(dto.identifier)
        if last_request and last_request.created_at >= now - timedelta(minutes=self.wait_minutes):
            raise WaitTimeException(f"کد تایید قبلاً ارسال شده است. لطفاً {self.wait_minutes} دقیقه صبر کنید.")

        code = str(random.randint(100000, 999999)) if dto.is_email_reset else str(random.randint(10000, 99999))

        otp_request = OTPRequest(
            identifier=dto.identifier,
            code=code,
            ip_address=dto.ip_address
        )
        self.otp_repo.save_request(otp_request)

        if dto.is_email_reset:
            success = self.email_provider.send_password_reset(dto.identifier, code)
            if not success:
                self.otp_repo.delete_request(otp_request)
                raise ValidationException("خطا در ارسال ایمیل. لطفاً بررسی کنید ایمیل صحیح است یا دقایقی دیگر تلاش کنید.")
        else:
            success = self.sms_provider.send_verification_code(dto.identifier, code)
            if not success:
                self.otp_repo.delete_request(otp_request)
                raise ValidationException("خطا در ارتباط با سرویس پیامکی. لطفاً دقایقی دیگر تلاش کنید.")

        DomainEventPublisher.publish("OTPRequested", {"identifier": dto.identifier})
        
        from users.tasks.cleanup import cleanup_expired_otps
        cleanup_expired_otps.apply_async((str(otp_request.uuid),), countdown=self.wait_minutes * 60)