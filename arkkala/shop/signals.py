from typing import Any
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from shop.models.product import Product, PriceHistory
from shop.models.category import Category
from shop.models.brand import Brand
from shop.infrastructure.cache.keys import CacheKeys
from platform_tools.services.cache import CacheStrategy

@receiver(post_save, sender=Product)
def track_price_changes(sender: Any, instance: Product, **kwargs: Any) -> None:
    """Logs product price mutability natively."""
    last_record = instance.price_history.order_by('-created_at').first()
    if not last_record or last_record.price != instance.base_price:
        PriceHistory.objects.create(product=instance, price=instance.base_price)

@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Brand)
@receiver([post_save, post_delete], sender=Product)
def invalidate_shop_caches(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Surgically invalidates dependent keys upon state mutation."""
    CacheStrategy(prefix="shop:product").invalidate(CacheKeys.MAX_PRICE)
    cache.delete(CacheKeys.GLOBAL_CATEGORY_MEGA_MENU)
    cache.delete(CacheKeys.HOME_PAGE_AGGREGATED)