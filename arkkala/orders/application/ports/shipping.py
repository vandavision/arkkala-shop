from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List
from orders.models.cart import CartItem


class ShippingProvider(ABC):
    """Port for external shipping calculation services."""
    
    @abstractmethod
    def calculate_cost(self, items: List[CartItem], dest_province: str, total_weight_grams: int) -> Decimal:
        pass