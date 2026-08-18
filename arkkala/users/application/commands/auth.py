import random
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from users.repositories.user import UserRepository
from users.repositories.otp import OTPRepository
from users.application.dtos import (
    OTPSendDTO, OTPVerifyDTO, EmailRegisterDTO, 
    EmailLoginDTO, PasswordResetConfirmDTO
)
from users.events.publishers import DomainEventPublisher
from users.services.sms import KavenegarService
from users.models.otp import OTPRequest
from users.tasks import cleanup_expired_otps

from shop.services.interaction import InteractionService
from orders.services.cart import CartService

User = get_user_model()

class AuthCommandService:
    """
    CQRS Write Operations explicitly delegating application authentication rules.
    """
    user_repo = UserRepository()
    otp_repo = OTPRepository()

    @classmethod
    def _merge_guest_data(cls, user: User, guest_id: Optional[str], client_ip: Optional[str] = None) -> None:
        """
        Bridges cross-domain interactions mapping history to verified entities effectively.
        """
        guest_ids = [g for g in [guest_id, client_ip] if g]
        if guest_ids:
            InteractionService.merge_guest_history_to_user(user, guest_ids)
            
        if guest_id:
            CartService.merge_guest_cart_to_user_cart(user, guest_id)

    @classmethod
    def send_otp(cls, dto: OTPSendDTO) -> None:
        """
        Enforces security restrictions mapping temporal traffic handling securely.
        """
        now = timezone.now()
        wait_time: int = getattr(settings, 'OTP_WAIT_TIME_MINUTES', 2)
        max_daily: int = getattr(settings, 'OTP_MAX_DAILY_REQUESTS', 5)

        daily_count: int = cls.otp_repo.count_recent_requests(dto.identifier, now - timedelta(hours=24))
        if daily_count >= max_daily:
            raise ValueError("شما بیش از حد مجاز درخواست داده‌اید. لطفاً ۲۴ ساعت دیگر تلاش کنید.")

        last_request = cls.otp_repo.get_last_request(dto.identifier)
        if last_request and last_request.created_at >= now - timedelta(minutes=wait_time):
            raise ValueError(f"کد تایید قبلاً ارسال شده است. لطفاً {wait_time} دقیقه صبر کنید.")

        code: str = str(random.randint(100000, 999999)) if dto.is_email_reset else str(random.randint(10000, 99999))

        otp_obj = OTPRequest(
            identifier=dto.identifier,
            code=code,
            ip_address=dto.ip_address
        )
        cls.otp_repo.save(otp_obj)

        if dto.is_email_reset:
            try:
                send_mail(
                    subject='بازیابی رمز عبور ارک کالا',
                    message=f'کد بازیابی رمز عبور شما:\n\n{code}',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@arkkala.com'),
                    recipient_list=[dto.identifier],
                    fail_silently=False,
                )
            except Exception:
                cls.otp_repo.delete(otp_obj)
                raise ValueError("خطا در ارسال ایمیل. لطفاً بررسی کنید ایمیل صحیح است یا دقایقی دیگر تلاش کنید.")
        else:
            if not KavenegarService.send_otp(dto.identifier, code):
                cls.otp_repo.delete(otp_obj)
                raise ValueError("خطا در ارتباط با سرویس پیامکی. لطفاً دقایقی دیگر تلاش کنید.")

        DomainEventPublisher.publish("OTPRequested", {"identifier": dto.identifier})
        cleanup_expired_otps.apply_async((str(otp_obj.uuid),), countdown=wait_time * 60)

    @classmethod
    def verify_otp_and_login(cls, dto: OTPVerifyDTO) -> Dict[str, Any]:
        """
        Completes authentication dynamically executing integration operations strictly.
        """
        otp_request = cls.otp_repo.get_valid_otp(dto.identifier, dto.code)
        if not otp_request:
            raise ValueError("کد وارد شده نامعتبر یا منقضی شده است.")

        otp_request.is_used = True
        cls.otp_repo.save(otp_request)

        user, created = cls.user_repo.get_or_create_by_phone(dto.identifier)
        cls.otp_repo.delete(otp_request)

        cls._merge_guest_data(user, dto.guest_id, dto.client_ip)

        if created:
            DomainEventPublisher.publish("UserRegisteredViaOTP", {"user_id": user.id})
        DomainEventPublisher.publish("UserLoggedIn", {"user_id": user.id})

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_new_user': created
        }

    @classmethod
    def register_email(cls, dto: EmailRegisterDTO) -> User:
        """
        Provisions identity creation validating structural isolation permanently.
        """
        if cls.user_repo.get_by_email(dto.email):
            raise ValueError("این ایمیل قبلاً ثبت شده است.")

        user = User(username=dto.email, email=dto.email)
        user.set_password(dto.password)
        cls.user_repo.save(user)

        cls._merge_guest_data(user, dto.guest_id, dto.client_ip)

        DomainEventPublisher.publish("UserRegisteredViaEmail", {"user_id": user.id})
        return user

    @classmethod
    def login_email(cls, dto: EmailLoginDTO) -> Dict[str, Any]:
        """
        Consumes explicit payload constraints establishing verified JWT tokens cleanly.
        """
        user = cls.user_repo.get_by_email(dto.email)
        if not user or not user.check_password(dto.password):
            raise ValueError("ایمیل یا رمز عبور اشتباه است.")

        cls._merge_guest_data(user, dto.guest_id, dto.client_ip)

        DomainEventPublisher.publish("UserLoggedIn", {"user_id": user.id})

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    @classmethod
    def verify_reset_code_and_set_password(cls, dto: PasswordResetConfirmDTO) -> None:
        """
        Resolves hash overrides enforcing absolute identity constraints flawlessly.
        """
        otp_request = cls.otp_repo.get_valid_otp(dto.email, dto.code)
        if not otp_request:
            raise ValueError("کد تایید نامعتبر یا منقضی شده است.")

        user = cls.user_repo.get_by_email(dto.email)
        if not user:
            raise ValueError("کاربری با این ایمیل یافت نشد.")

        user.set_password(dto.new_password)
        cls.user_repo.save(user)
        cls.otp_repo.delete(otp_request)
        DomainEventPublisher.publish("UserPasswordReset", {"user_id": user.id})