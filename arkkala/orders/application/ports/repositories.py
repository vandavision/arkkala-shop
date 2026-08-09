from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from orders.models.cart import Cart, CartItem
from orders.models.order import Order, OrderRequest
from orders.models.coupon import Coupon
from orders.models.shipping import ShippingMethod


class CartRepository(ABC):
    """Port for cart data access."""
    
    @abstractmethod
    def get_or_create_cart(self, user_id: Optional[int], guest_id: Optional[str]) -> Cart:
        pass

    @abstractmethod
    def get_cart_items_with_relations(self, cart: Cart) -> List[CartItem]:
        pass

    @abstractmethod
    def get_cart_totals(self, cart_items: List[CartItem]) -> Tuple[Decimal, int]:
        pass

    @abstractmethod
    def clear_cart(self, cart: Cart) -> None:
        pass


class OrderRepository(ABC):
    """Port for order data access."""
    
    @abstractmethod
    def create_order(self, order_data: dict) -> Order:
        pass

    @abstractmethod
    def create_order_items(self, order_items_data: List[dict]) -> None:
        pass

    @abstractmethod
    def get_user_order(self, user_id: int, order_uuid: str) -> Optional[Order]:
        pass

    @abstractmethod
    def create_order_request(self, order: Order, request_type: str, reason: str) -> OrderRequest:
        pass


class CouponRepository(ABC):
    """Port for coupon data access."""
    
    @abstractmethod
    def get_valid_coupon(self, code: str, lock: bool = False) -> Optional[Coupon]:
        pass

    @abstractmethod
    def increment_usage(self, coupon: Coupon) -> None:
        pass


class ShippingRepository(ABC):
    """Port for shipping methods data access."""
    
    @abstractmethod
    def get_shipping_method(self, method_id: str) -> Optional[ShippingMethod]:
        pass


class InventoryRepository(ABC):
    """Port for cross-domain inventory access."""
    
    @abstractmethod
    def lock_and_deduct_inventory(self, product_id: str, variant_id: Optional[str], quantity: int) -> None:
        pass


class CustomerRepository(ABC):
    """Port for cross-domain user resolution."""
    
    @abstractmethod
    def resolve_checkout_user(self, user_id: Optional[int], guest_data: dict) -> Tuple[Optional[AbstractUser], bool]:
        pass