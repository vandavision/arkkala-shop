from platform_tools.services.cache import CacheStrategy
from shop.application.ports.repositories import ProductRepositoryPort
from shop.infrastructure.cache.keys import CacheKeys

class GetMaxPriceQuery:
    """Reads the maximum product price, highly optimized via cache."""

    def __init__(self, product_repo: ProductRepositoryPort) -> None:
        self.product_repo = product_repo
        self.cache_strategy = CacheStrategy(prefix="shop:product")

    def execute(self) -> int:
        """Fetches from cache or resolves from database via port."""
        return self.cache_strategy.get_or_set(
            key=CacheKeys.MAX_PRICE, 
            query_func=self.product_repo.get_max_base_price
        )