from typing import Any, Dict
from django.db.models import Max
from django.db.models.query import QuerySet
from shop.models.product import Product
from platform_tools.services.cache import CacheStrategy
from platform_tools.utils.profiler import QueryProfiler

class ProductQueryService:
    """
    CQRS Read Operations. Strictly no database modifications here.
    """
    cache_strategy = CacheStrategy(prefix="shop:product")

    @classmethod
    @QueryProfiler(analyze=False)
    def get_optimized_products(cls, user: Any) -> QuerySet:
        qs: QuerySet = Product.objects.active().with_relations().with_approved_feedback()
        return qs.with_user_favorite(user)

    @classmethod
    def get_max_price(cls) -> int:
        def fetch_max() -> int:
            result: Dict[str, Any] = Product.objects.filter(is_active=True).aggregate(max_price=Max('base_price'))
            return int(result.get('max_price') or 0)
        return cls.cache_strategy.get_or_set(key="max_price", query_func=fetch_max)