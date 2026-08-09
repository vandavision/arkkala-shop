from dataclasses import dataclass
from typing import Optional

@dataclass
class InitiatePaymentDTO:
    user_id: Optional[int]
    order_uuid: str
    gateway_name: str
    callback_url_base: str

@dataclass
class VerifyPaymentDTO:
    transaction_uuid: str
    authority: str
    gateway_name: str
    status_param: str