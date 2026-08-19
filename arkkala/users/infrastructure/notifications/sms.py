import requests
import logging
from django.conf import settings
from users.application.ports.notifications import SMSProviderPort

logger = logging.getLogger(__name__)

class KavenegarSMSProvider(SMSProviderPort):
    """
    Infrastructure implementation corresponding to Kavenegar API boundaries definitively.
    """
    def send_verification_code(self, phone_number: str, code: str) -> bool:
        api_key: str = getattr(settings, 'KAVENEGAR_API_KEY', '')
        template: str = getattr(settings, 'KAVENEGAR_OTP_TEMPLATE', 'verify')
        
        if not api_key or api_key == 'your_kavenegar_api_key_here':
            logger.info(f"MOCK SMS: Code {code} sent to {phone_number}")
            return True

        url: str = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"
        payload: dict = {
            'receptor': phone_number,
            'token': code,
            'template': template
        }
        try:
            response = requests.post(url, data=payload, timeout=5)
            if response.status_code == 200:
                return True
            logger.error(f"Kavenegar API Error: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Kavenegar Request Failed: {e}")
            return False