from typing import Any, Optional
from django.db.models import F
from django.db.models import QuerySet
from shop.models.product import Product
from shop.models.interaction import Comment, Question, UserProductHistory
from shop.application.ports.repositories import InteractionRepositoryPort

class DjangoInteractionRepository(InteractionRepositoryPort):
    """Django ORM Implementation of Interaction Repository Port."""

    def save_comment(self, comment: Comment) -> Comment:
        """Saves a comment instance to the database."""
        comment.save()
        return comment

    def save_question(self, question: Question) -> Question:
        """Saves a question instance to the database."""
        question.save()
        return question

    def get_user_comments(self, user: Any) -> QuerySet:
        """Fetches isolated comments for the authenticated user."""
        return Comment.objects.filter(user=user).select_related('product').order_by('-created_at')

    def save_user_product_history(self, product: Product, user: Any = None, guest_id: Optional[str] = None) -> UserProductHistory:
        """Records or updates the history of a user or guest viewing a product."""
        if not user and not guest_id:
            raise ValueError("شناسه کاربر یا مهمان الزامی است.")

        filters = {'product': product}
        if user and user.is_authenticated:
            filters['user'] = user
        else:
            filters['guest_id'] = guest_id

        history, created = UserProductHistory.objects.get_or_create(
            **filters,
            defaults={'view_count': 1}
        )
        
        if not created:
            history.view_count = F('view_count') + 1
            history.save(update_fields=['view_count', 'modified_at'])
            
        return history