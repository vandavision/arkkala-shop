from typing import Optional
from orders.models.shipping import ShippingMethod
from orders.application.ports.repositories import ShippingRepository


class DjangoShippingRepository(ShippingRepository):
    """Django ORM implementation of ShippingRepository."""

    def get_shipping_method(self, method_id: str) -> Optional[ShippingMethod]:
        return ShippingMethod.objects.filter(pk=method_id, is_active=True).first()