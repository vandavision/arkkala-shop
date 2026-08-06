from typing import Dict, Any
from shop.repositories.product import ProductRepository
from shop.events.publishers import DomainEventPublisher

class ProductCommandService:
    """
    CQRS Write Operations. Strictly logic execution and state mutation.
    """
    repository = ProductRepository()

    @classmethod
    def increment_view_count(cls, product_slug: str) -> None:
        """
        Calls atomic repository operation and triggers domain event.
        """
        if cls.repository.increment_view_count(product_slug):
            DomainEventPublisher.publish("ProductViewed", {"product_slug": product_slug})

    @classmethod
    def toggle_favorite(cls, product_slug: str, user_id: Any) -> Dict[str, Any]:
        """
        Toggles state and acts as a boundary for business rules.
        """
        is_added: bool = cls.repository.toggle_favorite(product_slug, user_id)
        
        if is_added:
            DomainEventPublisher.publish("ProductFavorited", {"product_slug": product_slug, "user_id": user_id})
            return {"is_favorite": True, "message": "کالا به لیست علاقه‌مندی‌های شما اضافه شد."}
        else:
            DomainEventPublisher.publish("ProductUnfavorited", {"product_slug": product_slug, "user_id": user_id})
            return {"is_favorite": False, "message": "کالا از علاقه‌مندی‌های شما حذف شد."}