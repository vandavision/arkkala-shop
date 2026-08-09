from typing import Any
from django.db.models import QuerySet
from shop.application.ports.repositories import InteractionRepositoryPort

class GetUserCommentsQuery:
    """Retrieves isolated comments for a specific user."""

    def __init__(self, interaction_repo: InteractionRepositoryPort) -> None:
        self.interaction_repo = interaction_repo

    def execute(self, user: Any) -> QuerySet:
        """Returns the queryset of comments for the user."""
        return self.interaction_repo.get_user_comments(user)