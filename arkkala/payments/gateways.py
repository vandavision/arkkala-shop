"""
Payment Gateways Implementation.
Uses Strategy and Factory patterns to allow adding multiple gateways seamlessly.
"""
import requests
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
from django.conf import settings


class PaymentException(Exception):
    """Custom exception for payment gateway errors."""
    pass


class BaseGateway(ABC):
    """Abstract Base Class for all payment gateways."""
    
    @abstractmethod
    def request_payment(self, amount: int, callback_url: str, description: str, **kwargs) -> Tuple[str, str]:
        """
        Initiate a payment request.
        Returns:
            Tuple[str, str]: (payment_redirect_url, authority_or_token)
        """
        pass

    @abstractmethod
    def verify_payment(self, authority: str, amount: int, **kwargs) -> Tuple[bool, str]:
        """
        Verify the payment after user returns from gateway.
        Returns:
            Tuple[bool, str]: (is_successful, ref_id_or_error_message)
        """
        pass


class ZarinpalGateway(BaseGateway):
    """Zarinpal Gateway Implementation."""
    
    def __init__(self) -> None:
        self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '00000000-0000-0000-0000-000000000000')
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
                raise PaymentException(f"Zarinpal Error: {response_data.get('errors')}")
        except Exception as e:
            raise PaymentException(f"Gateway request failed: {str(e)}")

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
                return False, str(response_data.get('errors', 'Unknown Verification Error'))
        except Exception as e:
            return False, str(e)


class GatewayFactory:
    """Factory to get the requested gateway instance."""
    
    @staticmethod
    def get_gateway(gateway_name: str) -> BaseGateway:
        gateways: Dict[str, Any] = {
            'zarinpal': ZarinpalGateway,
            # 'saman': SamanGateway,
            # 'mellat': MellatGateway,
        }
        if gateway_name not in gateways:
            raise ValueError(f"Gateway '{gateway_name}' is not supported.")
        return gateways[gateway_name]()