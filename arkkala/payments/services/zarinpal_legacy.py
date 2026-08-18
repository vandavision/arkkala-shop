import requests
from abc import ABC, abstractmethod
from typing import Tuple
from django.conf import settings

class BaseGateway(ABC):
    @abstractmethod
    def request_payment(self, amount: int, callback_url: str, description: str, **kwargs) -> Tuple[str, str]:
        pass

    @abstractmethod
    def verify_payment(self, authority: str, amount: int, **kwargs) -> Tuple[bool, str]:
        pass

class ZarinpalGateway(BaseGateway):
    def __init__(self) -> None:
        self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', "2c86f44c-1b94-41eb-8b88-6f12971c639a")
        self.sandbox = getattr(settings, 'ZARINPAL_SANDBOX', True)
        subdomain = "sandbox" if self.sandbox else "api"
        self.request_url = f"https://{subdomain}.zarinpal.com/pg/v4/payment/request.json"
        self.verify_url = f"https://{subdomain}.zarinpal.com/pg/v4/payment/verify.json"
        self.start_pay_url = f"https://{subdomain}.zarinpal.com/pg/StartPay/"

    def request_payment(self, amount: int, callback_url: str, description: str, **kwargs) -> Tuple[str, str]:
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10,
            "currency": "IRT",
            "description": description,
            "callback_url": callback_url,
        }

        try:
            res = requests.post(self.request_url, json=data, timeout=10)
            res.raise_for_status()
            response_data = res.json()

            if response_data.get('data') and response_data['data'].get('code') == 100:
                authority = response_data['data']['authority']
                payment_url = self.start_pay_url + authority
                return payment_url, authority
            else:
                error_details = response_data.get('errors') or 'اطلاعات مرچنت یا مبلغ نامعتبر است'
                raise Exception(f"خطای زرین‌پال: {error_details}")
                
        except requests.exceptions.RequestException:
            raise Exception("ارتباط با سرورهای زرین‌پال برقرار نشد. لطفاً دقایقی دیگر تلاش کنید.")
        except Exception as e:
            raise Exception(f"خطا در ایجاد تراکنش: {str(e)}")

    def verify_payment(self, authority: str, amount: int, **kwargs) -> Tuple[bool, str]:
        data = {
            "merchant_id": self.merchant_id,
            "amount": amount * 10,
            "authority": authority,
        }

        try:
            res = requests.post(self.verify_url, json=data, timeout=10)
            res.raise_for_status()
            response_data = res.json()

            if response_data.get('data') and response_data['data'].get('code') in [100, 101]:
                return True, str(response_data['data']['ref_id'])
            else:
                return False, str(response_data.get('errors', 'خطای ناشناخته در تایید تراکنش'))
        except Exception as e:
            return False, f"خطا در ارتباط با زرین‌پال: {str(e)}"