import logging
from typing import List, Dict, Any
from decimal import Decimal
import requests
from django.conf import settings

from orders.models import CartItem
from .cart import CartService

logger = logging.getLogger(__name__)


class ShippingCalculatorService:
    """Local algorithm for fallback shipping calculation."""
    @staticmethod
    def calculate_post_cost(total_weight_grams: int, origin_province: str, dest_province: str) -> Decimal:
        base_post_cost: int = 35000
        weight_penalty: int = (total_weight_grams // 500) * 5000
        distance_multiplier: float = 1.0 if origin_province == dest_province else 1.35
        final_cost: float = (base_post_cost + weight_penalty) * distance_multiplier
        return Decimal(int(final_cost))


class PostexShippingService:
    """External API integration for shipping."""
    BASE_URL: str = getattr(settings, 'POSTEX_BASE_URL', 'https://api.postex.ir')
    API_KEY: str = getattr(settings, 'POSTEX_API_KEY', '')
    FROM_CITY_CODE: int = getattr(settings, 'POSTEX_FROM_CITY_CODE', 1)

    @classmethod
    def calculate_shipping_cost(cls, cart_items: List[CartItem], dest_province: str, total_weight_grams: int) -> Decimal:
        parcels_payload: List[Dict[str, Any]] = [
            {
                "length": int(getattr(item.product, 'volume', 1000) ** (1/3)) or 10,
                "width": int(getattr(item.product, 'volume', 1000) ** (1/3)) or 10,
                "height": int(getattr(item.product, 'volume', 1000) ** (1/3)) or 10,
                "total_weight": CartService.calculate_item_weight(item) * item.quantity,
                "is_fragile": getattr(item.product, 'is_fragile', False),
                "is_liquid": getattr(item.product, 'is_liquid', False),
                "total_value": float(CartService.calculate_item_price(item) * item.quantity),
                "pre_paid_amount": 0,
                "total_value_currency": "IRR",
                "box_type_id": 0
            } for item in cart_items
        ]

        payload = {
            "collection_type": "pick_up",
            "from_city_code": cls.FROM_CITY_CODE,
            "courier": {"courier_code": "post", "service_type": "pishtaz"},
            "parcels": parcels_payload,
            "value_added_service": {"request_label": False, "request_packaging": False, "request_sms_notification": True}
        }

        try:
            if not cls.API_KEY:
                raise ValueError("API Key is not configured.")

            response = requests.post(f"{cls.BASE_URL}/api/v1/shipping/quotes", json=payload, headers={"x-api-key": cls.API_KEY, "Content-Type": "application/json"}, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list) and data:
                return Decimal(int(data[0].get('price', 0) or data[0].get('cost', 0)))
            if isinstance(data, dict):
                return Decimal(int(data.get('amount', 0) or data.get('total_amount', 0)))
            
            raise ValueError("فرمت پاسخ جی‌سان پستکس معتبر نیست.")

        except Exception as e:
            logger.error(f"Postex API Error: {str(e)}. Falling back to algorithmic calculation.")
            return ShippingCalculatorService.calculate_post_cost(total_weight_grams, "تهران", dest_province)