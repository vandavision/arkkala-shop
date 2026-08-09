from django.contrib.auth import get_user_model
from django.db import transaction
from shop.models.interaction import Comment
from shop.domain.exceptions import ProductNotFoundError
from shop.domain.events import CommentCreatedEvent
from shop.application.dto.commands import CreateCommentCommandDTO
from shop.application.ports.repositories import ProductRepositoryPort, InteractionRepositoryPort
from shop.application.ports.event_bus import EventBusPort

User = get_user_model()

class CreateCommentCommand:
    """Executes the creation of a product comment with strict isolation."""
    
    def __init__(self, 
                 product_repo: ProductRepositoryPort, 
                 interaction_repo: InteractionRepositoryPort, 
                 event_bus: EventBusPort) -> None:
        self.product_repo = product_repo
        self.interaction_repo = interaction_repo
        self.event_bus = event_bus

    @transaction.atomic
    def execute(self, dto: CreateCommentCommandDTO) -> Comment:
        """Validates payload, mutates state, and defers event to on_commit."""
        product = self.product_repo.get_by_slug(dto.product_slug)
        if not product:
            raise ProductNotFoundError("محصول مورد نظر یافت نشد.")

        user = User.objects.filter(id=dto.user_id).first() if dto.user_id else None

        comment = Comment(
            product=product,
            user=user,
            body=dto.body,
            rating=dto.rating
        )
        comment.full_clean()
        saved_comment = self.interaction_repo.save_comment(comment)

        self.event_bus.publish(CommentCreatedEvent(comment_uuid=str(saved_comment.uuid)))
        return saved_comment