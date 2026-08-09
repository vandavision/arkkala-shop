from django.contrib.auth import get_user_model
from django.db import transaction
from shop.models.interaction import Question
from shop.domain.exceptions import ProductNotFoundError
from shop.domain.events import QuestionCreatedEvent
from shop.application.dto.commands import CreateQuestionCommandDTO
from shop.application.ports.repositories import ProductRepositoryPort, InteractionRepositoryPort
from shop.application.ports.event_bus import EventBusPort

User = get_user_model()

class CreateQuestionCommand:
    """Executes the creation of a product question."""
    
    def __init__(self, 
                 product_repo: ProductRepositoryPort, 
                 interaction_repo: InteractionRepositoryPort, 
                 event_bus: EventBusPort) -> None:
        self.product_repo = product_repo
        self.interaction_repo = interaction_repo
        self.event_bus = event_bus

    @transaction.atomic
    def execute(self, dto: CreateQuestionCommandDTO) -> Question:
        """Validates payload, mutates state, and defers event to on_commit."""
        product = self.product_repo.get_by_slug(dto.product_slug)
        if not product:
            raise ProductNotFoundError("محصول مورد نظر یافت نشد.")

        user = User.objects.filter(id=dto.user_id).first() if dto.user_id else None

        question = Question(
            product=product,
            user=user,
            name=dto.guest_name if not user else None,
            text=dto.body
        )
        question.full_clean()
        saved_question = self.interaction_repo.save_question(question)

        self.event_bus.publish(QuestionCreatedEvent(question_uuid=str(saved_question.uuid)))
        return saved_question