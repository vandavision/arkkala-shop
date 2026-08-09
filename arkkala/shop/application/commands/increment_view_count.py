from shop.application.ports.repositories import ProductRepositoryPort
from shop.application.ports.event_bus import EventBusPort
from shop.domain.events import ProductViewedEvent

class IncrementViewCountCommand:
    """Handles the atomic update of a product's view count."""

    def __init__(self, product_repo: ProductRepositoryPort, event_bus: EventBusPort) -> None:
        self.product_repo = product_repo
        self.event_bus = event_bus

    def execute(self, product_slug: str) -> None:
        """Executes the increment and triggers the domain event."""
        if self.product_repo.increment_view_count(product_slug):
            self.event_bus.publish(ProductViewedEvent(product_slug=product_slug))