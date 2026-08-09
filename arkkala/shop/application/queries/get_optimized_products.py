from typing import Any
from django.db.models import QuerySet
from shop.application.ports.repositories import ProductRepositoryPort

class GetOptimizedProductsQuery:
    """Prepares the product listing with eager loaded relationships."""

    def __init__(self, product_repo: ProductRepositoryPort) -> None:
        self.product_repo = product_repo

    def execute(self, user: Any) -> QuerySet:
        """Returns the fully optimized queryset."""
        return self.product_repo.get_active_products_optimized(user)