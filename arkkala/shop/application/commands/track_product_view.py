from django.contrib.auth import get_user_model
from django.db import transaction
from shop.domain.exceptions import ProductNotFoundError
from shop.domain.events import UserViewedProductEvent
from shop.application.dto.commands import TrackProductViewDTO
from shop.application.ports.repositories import ProductRepositoryPort, InteractionRepositoryPort
from shop.application.ports.event_bus import EventBusPort

User = get_user_model()

class TrackProductViewCommand:
    """Executes the logging of a user or guest product view action."""

    def __init__(self, 
                 product_repo: ProductRepositoryPort, 
                 interaction_repo: InteractionRepositoryPort, 
                 event_bus: EventBusPort) -> None:
        self.product_repo = product_repo
        self.interaction_repo = interaction_repo
        self.event_bus = event_bus

    @transaction.atomic
    def execute(self, dto: TrackProductViewDTO) -> None:
        """Resolves identity and product, saves history, and dispatches the domain event."""
        if not dto.user_id and not dto.guest_id:
            return

        product = self.product_repo.get_by_slug(dto.product_slug)
        if not product:
            raise ProductNotFoundError("محصول یافت نشد.")

        user = User.objects.filter(id=dto.user_id).first() if dto.user_id else None

        self.interaction_repo.save_user_product_history(product, user, dto.guest_id)
        
        if user:
            self.event_bus.publish(UserViewedProductEvent(user_id=dto.user_id, product_slug=dto.product_slug))