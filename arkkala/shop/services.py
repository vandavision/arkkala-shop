"""
Service Layer for Shop App.
Handles business logic separated from Views and Models.
"""
from django.db.models import F, Max
from django.contrib.auth import get_user_model
from .models import Product, Comment, Question
from typing import Any, Optional
User = get_user_model()


class ProductService:
    """Service class for handling product-related business logic."""
    
    @staticmethod
    def get_max_price() -> int:
        """
        Calculates and returns the maximum base_price among all products.
        
        Returns:
            int: The maximum price. Returns 0 if no products are found.
        """
        result = Product.objects.aggregate(max_price=Max('base_price'))
        return int(result.get('max_price') or 0)

    @staticmethod
    def increment_view_count(product: Product) -> None:
        """
        Increments the view count of a product atomically.
        
        Args:
            product (Product): The product instance to update.
        """
        Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)
        product.refresh_from_db(fields=['view_count'])

    @staticmethod
    def add_comment(product: Product, user: User | None, body: str, rating: int) -> Comment:
        """
        Adds a new comment to a product.
        
        Args:
            product (Product): The product to comment on.
            user (User | None): The user submitting the comment (or None for anonymous).
            body (str): The comment text.
            rating (int): The rating given by the user (1-5).
            
        Returns:
            Comment: The newly created comment instance.
        """
        return Comment.objects.create(
            product=product,
            user=user,
            body=body,
            rating=rating
        )


class QuestionService:
    """
    Service Layer to handle business logic for product questions and answers.
    """
    @staticmethod
    def add_question(product: Product, text: str, user: Optional[Any] = None, name: Optional[str] = None) -> Question:
        """
        Creates a new question for a product. Supports both authenticated and guest users.
        """
        return Question.objects.create(
            product=product,
            user=user if user and user.is_authenticated else None,
            name=name if not (user and user.is_authenticated) else None,
            text=text
        )