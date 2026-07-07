"""
Service Layer for User Authentication (Kavenegar & Anti-Spam Logic).
"""
import random
import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTPRequest
from .tasks import cleanup_expired_otps

logger = logging.getLogger(__name__)


class KavenegarService:
    """Service to handle SMS sending via Kavenegar lookup API."""
    
    @staticmethod
    def send_otp(phone_number: str, code: str) -> bool:
        api_key = getattr(settings, 'KAVENEGAR_API_KEY', '')
        template = getattr(settings, 'KAVENEGAR_OTP_TEMPLATE', 'verify')
        
        if not api_key or api_key == 'YOUR_API_KEY':
            logger.info(f"MOCK SMS: Code {code} sent to {phone_number}")
            # For local development without API key, we return True to simulate success
            return True

        url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"
        payload = {
            'receptor': phone_number,
            'token': code,
            'template': template
        }
        try:
            response = requests.post(url, data=payload, timeout=5)
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Kavenegar API Error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Kavenegar Request Failed: {e}")
            return False


class OTPAuthService:
    """Business logic for generating, verifying OTPs, and managing security."""
    
    @staticmethod
    def generate_and_send_otp(phone_number: str, ip_address: str) -> None:
        now = timezone.now()
        wait_time = getattr(settings, 'OTP_WAIT_TIME_MINUTES', 2)
        max_daily = getattr(settings, 'OTP_MAX_DAILY_REQUESTS', 5)
        
        # 1. Anti-Spam Check (Max requests per 24 hours per phone number)
        daily_requests = OTPRequest.objects.filter(
            phone_number=phone_number,
            created_at__gte=now - timedelta(hours=24)
        )
        if daily_requests.count() >= max_daily:
            raise ValueError(f"شما بیش از حد مجاز درخواست داده‌اید. لطفاً ۲۴ ساعت دیگر تلاش کنید.")
            
        # 2. Rate Limiting Check (Wait time between requests)
        last_request = daily_requests.order_by('-created_at').first()
        if last_request and last_request.created_at >= now - timedelta(minutes=wait_time):
            raise ValueError(f"کد تایید قبلاً ارسال شده است. لطفاً {wait_time} دقیقه صبر کنید.")

        # Generate 5-digit verification code
        code = str(random.randint(10000, 99999))
        
        # Save Request to Database
        otp_obj = OTPRequest.objects.create(
            phone_number=phone_number,
            code=code,
            ip_address=ip_address
        )
        
        # Send SMS via Kavenegar
        is_sent = KavenegarService.send_otp(phone_number, code)
        if not is_sent:
            otp_obj.delete() # Rollback if SMS failed
            raise ValueError("خطا در ارتباط با سرویس پیامکی. لطفاً دقایقی دیگر تلاش کنید.")

        # Schedule Celery task to delete this record from DB exactly after expiration
        cleanup_expired_otps.apply_async((str(otp_obj.uuid),), countdown=wait_time * 60)

    @staticmethod
    def verify_otp_and_login(phone_number: str, code: str) -> dict:
        now = timezone.now()
        
        otp_request = OTPRequest.objects.filter(
            phone_number=phone_number,
            code=code,
            is_used=False,
            expires_at__gte=now
        ).first()
        
        if not otp_request:
            raise ValueError("کد وارد شده نامعتبر یا منقضی شده است.")
            
        otp_request.is_used = True
        otp_request.save(update_fields=['is_used'])
        
        # Get or Create User seamlessly
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={'username': phone_number, 'is_active': True}
        )
        
        # We delete the OTP request immediately upon successful use to keep DB clean
        otp_request.delete()
        
        # Generate JWT Tokens
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_new_user': created
        }