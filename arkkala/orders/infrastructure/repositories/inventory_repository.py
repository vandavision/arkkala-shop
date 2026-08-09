from typing import Optional
from django.db.models import F
from shop.models.product import Product, ProductVariant
from orders.application.ports.repositories import InventoryRepository


class DjangoInventoryRepository(InventoryRepository):
    """Django ORM implementation for cross-domain inventory management."""

    def lock_and_deduct_inventory(self, product_id: str, variant_id: Optional[str], quantity: int) -> None:
        if variant_id:
            locked_variant = ProductVariant.objects.select_for_update().get(pk=variant_id)
            locked_variant.inventory = F('inventory') - quantity
            locked_variant.save(update_fields=['inventory'])
        else:
            locked_product = Product.objects.select_for_update().get(pk=product_id)
            locked_product.base_inventory = F('base_inventory') - quantity
            locked_product.save(update_fields=['base_inventory'])