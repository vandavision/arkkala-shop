from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from shop.models.interaction import Comment, Question
from shop.repositories.product import ProductRepository
from shop.events.publishers import DomainEventPublisher
from shop.application.dtos import InteractionCreateDTO

User = get_user_model()

class InteractionCommandService:
    """
    CQRS Write Operations for Comments and Questions.
    """
    product_repo = ProductRepository()

    @classmethod
    def create_comment(cls, dto: InteractionCreateDTO) -> Comment:
        product = cls.product_repo.get_by_slug(dto.product_slug)
        if not product:
            raise ValueError("Product not found")

        user = User.objects.filter(id=dto.user_id).first() if dto.user_id else None

        comment = Comment(
            product=product,
            user=user,
            body=dto.body,
            rating=dto.rating
        )
        comment.full_clean()  # Strictly enforce model validation rules
        comment.save()

        DomainEventPublisher.publish("CommentCreated", {"comment_uuid": str(comment.uuid)})
        return comment

    @classmethod
    def create_question(cls, dto: InteractionCreateDTO) -> Question:
        product = cls.product_repo.get_by_slug(dto.product_slug)
        if not product:
            raise ValueError("Product not found")

        user = User.objects.filter(id=dto.user_id).first() if dto.user_id else None

        question = Question(
            product=product,
            user=user,
            name=dto.name if not user else None,
            text=dto.body
        )
        question.full_clean()  # Strictly enforce model validation rules
        question.save()

        DomainEventPublisher.publish("QuestionCreated", {"question_uuid": str(question.uuid)})
        return question