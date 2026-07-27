# shop/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from shop.models.product import Product, PriceHistory
from shop.models.category import Category
from shop.models.brand import Brand


@receiver(post_save, sender=Product)
def track_price_changes(sender, instance: Product, **kwargs) -> None:
    last_record = instance.price_history.order_by('-created_at').first()
    if not last_record or last_record.price != instance.base_price:
        PriceHistory.objects.create(product=instance, price=instance.base_price)


@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Brand)
@receiver([post_save, post_delete], sender=Product)
def invalidate_shop_caches(sender, instance, **kwargs) -> None:
    cache.delete("global_category_mega_menu_tree")
    cache.delete("home_page_aggregated_data")