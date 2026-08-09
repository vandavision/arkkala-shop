from dataclasses import dataclass
from typing import Optional


@dataclass
class CheckoutAddressDTO:
    """DTO for shipping address details."""
    title: str
    country: str
    province: str
    city: str
    postal_address: str
    postal_code: str
    plaque: str
    building_unit: Optional[str]


@dataclass
class CheckoutGuestDTO:
    """DTO for guest customer information."""
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    password: Optional[str]


@dataclass
class CheckoutCommandDTO:
    """DTO for processing checkout."""
    user_id: Optional[int]
    guest_id: Optional[str]
    shipping_method_id: str
    coupon_code: Optional[str]
    address: CheckoutAddressDTO
    guest_data: CheckoutGuestDTO


@dataclass
class OrderRequestCommandDTO:
    """DTO for order cancellation or return requests."""
    user_id: int
    order_uuid: str
    request_type: str
    reason: str