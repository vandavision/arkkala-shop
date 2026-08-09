from typing import Dict, Any
from shop.domain.exceptions import ProductNotFoundError
from shop.domain.events import ProductFavoritedEvent, ProductUnfavoritedEvent
from shop.application.ports.repositories import ProductRepositoryPort
from shop.application.ports.event_bus import EventBusPort

class ToggleFavoriteCommand:
    """Toggles product favorite status for a given user."""

    def __init__(self, product_repo: ProductRepositoryPort, event_bus: EventBusPort) -> None:
        self.product_repo = product_repo
        self.event_bus = event_bus

    def execute(self, product_slug: str, user_id: Any) -> Dict[str, Any]:
        """Executes the toggle logic and returns structured state feedback."""
        try:
            is_added = self.product_repo.toggle_favorite(product_slug, user_id)
        except ValueError:
            raise ProductNotFoundError("محصول مورد نظر یافت نشد.")

        if is_added:
            self.event_bus.publish(ProductFavoritedEvent(product_slug=product_slug, user_id=user_id))
            return {"is_favorite": True, "message": "کالا به لیست علاقه‌مندی‌های شما اضافه شد."}
        
        self.event_bus.publish(ProductUnfavoritedEvent(product_slug=product_slug, user_id=user_id))
        return {"is_favorite": False, "message": "کالا از علاقه‌مندی‌های شما حذف شد."}