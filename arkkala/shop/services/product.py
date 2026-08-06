from typing import Any, Dict
from django.db.models import F, Max
from django.contrib.auth import get_user_model
from shop.models.product import Product
from platform_tools.services.cache import CacheStrategy

User = get_user_model()

class ProductService:
    """
    Encapsulated business logic and caching strategy for Product entities.
    """
    cache_strategy = CacheStrategy(prefix="shop:product")

    @classmethod
    def get_max_price(cls) -> int:
        """
        Retrieves the maximum product price, utilizing cache to avoid expensive DB aggregations.
        """
        def query_max_price() -> int:
            result = Product.objects.filter(is_active=True).aggregate(max_price=Max('base_price'))
            return int(result.get('max_price') or 0)

        return cls.cache_strategy.get_or_set(key="max_price", query_func=query_max_price)

    @classmethod
    def increment_view_count(cls, product: Product) -> None:
        """
        Increments the view count atomically directly in the database.
        """
        Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)
        product.refresh_from_db(fields=['view_count'])

    @classmethod
    def toggle_favorite(cls, product: Product, user: User) -> Dict[str, Any]:
        """
        Toggles user favorite status for a given product.
        """
        if product.favorites.filter(id=user.id).exists():
            product.favorites.remove(user)
            return {"is_favorite": False, "message": "کالا از علاقه‌مندی‌های شما حذف شد."}
        
        product.favorites.add(user)
        return {"is_favorite": True, "message": "کالا به لیست علاقه‌مندی‌های شما اضافه شد."}

    @classmethod
    def invalidate_product_caches(cls) -> None:
        """
        Clears product related cache keys upon updates.
        """
        cls.cache_strategy.invalidate("max_price")