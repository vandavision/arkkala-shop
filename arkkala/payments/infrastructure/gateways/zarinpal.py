from typing import Tuple
from payments.services.zarinpal_legacy import ZarinpalGateway as OriginalZarinpalGateway
from payments.application.ports.gateways import PaymentGatewayPort
from payments.domain.exceptions import PaymentGatewayException

class ZarinpalAdapter(PaymentGatewayPort):
    def __init__(self):
        self.gateway = OriginalZarinpalGateway()

    def request_payment(self, amount: int, callback_url: str, description: str) -> Tuple[str, str]:
        try:
            return self.gateway.request_payment(amount, callback_url, description)
        except Exception as e:
            raise PaymentGatewayException(str(e))

    def verify_payment(self, authority: str, amount: int) -> Tuple[bool, str]:
        return self.gateway.verify_payment(authority, amount)


def get_gateway_provider(name: str) -> PaymentGatewayPort:
    if name == 'zarinpal':
        return ZarinpalAdapter()
    raise ValueError(f"Gateway {name} not supported.")