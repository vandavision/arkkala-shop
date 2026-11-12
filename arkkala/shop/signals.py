from typing import Any
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from shop.models.product import Product, PriceHistory
from shop.models.category import Category
from shop.models.brand import Brand
from shop.infrastructure.cache.keys import CacheKeys
from platform_tools.services.cache import CacheStrategy
from platform_seo.models import SlugSwap


@receiver(pre_save, sender=Product)
@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=Brand)
def record_slug_swap_on_change(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Automatically records a SlugSwap entry when an entity's slug changes to preserve SEO equity."""
    if not instance.pk:
        return
    old_instance = sender.objects.filter(pk=instance.pk).only('slug').first()
    if old_instance and old_instance.slug and old_instance.slug != instance.slug:
        content_type = ContentType.objects.get_for_model(sender)
        # Update chained swaps pointing to the old slug so there are no redirect chains
        SlugSwap.objects.filter(
            content_type=content_type,
            new_slug=old_instance.slug
        ).update(new_slug=instance.slug)
        SlugSwap.objects.create(
            old_slug=old_instance.slug,
            new_slug=instance.slug,
            content_type=content_type,
            object_id=0,  # UUID models use slug + content_type lookup
        )


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