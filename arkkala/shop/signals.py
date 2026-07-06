from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, PriceHistory

@receiver(post_save, sender=Product)
def track_price_changes(sender, instance: Product, created: bool, **kwargs) -> None:
    """
    Automatically records the price of a product whenever it is created or its base_price changes.
    """
    last_record = instance.price_history.order_by('-created_at').first()
    
    if not last_record or last_record.price != instance.base_price:
        PriceHistory.objects.create(product=instance, price=instance.base_price)