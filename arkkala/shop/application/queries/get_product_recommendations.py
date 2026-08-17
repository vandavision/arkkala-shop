from typing import Any, Optional
from django.db.models import QuerySet
from shop.application.ports.repositories import ProductRepositoryPort

class GetProductRecommendationsQuery:
    """Retrieves personalized product recommendations based on identity."""

    def __init__(self, product_repo: ProductRepositoryPort) -> None:
        self.product_repo = product_repo

    def execute(self, user: Any, guest_id: Optional[str] = None) -> QuerySet:
        """Returns an optimized queryset of recommended products."""
        return self.product_repo.get_recommendations_for_user(user, guest_id)