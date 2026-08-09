from typing import Any
from django.db.models import QuerySet
from shop.models.interaction import Comment, Question
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