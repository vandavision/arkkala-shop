from abc import ABC, abstractmethod
from typing import Tuple

class PaymentGatewayPort(ABC):
    """Port for communicating with external payment gateways."""
    @abstractmethod
    def request_payment(self, amount: int, callback_url: str, description: str) -> Tuple[str, str]:
        pass

    @abstractmethod
    def verify_payment(self, authority: str, amount: int) -> Tuple[bool, str]:
        pass