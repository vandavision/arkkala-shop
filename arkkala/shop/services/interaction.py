from typing import Optional
from django.contrib.auth import get_user_model
from shop.models.product import Product
from shop.models.interaction import Comment, Question

User = get_user_model()

class InteractionService:
    """
    Business logic for Comments and Questions.
    """
    @classmethod
    def add_comment(cls, product: Product, user: Optional[User], body: str, rating: int) -> Comment:
        """
        Adds a comment to the specified product.
        """
        return Comment.objects.create(
            product=product,
            user=user,
            body=body,
            rating=rating
        )

    @classmethod
    def add_question(cls, product: Product, text: str, user: Optional[User] = None, name: Optional[str] = None) -> Question:
        """
        Adds a question to the specified product.
        """
        return Question.objects.create(
            product=product,
            user=user if user and user.is_authenticated else None,
            name=name if not (user and user.is_authenticated) else None,
            text=text
        )