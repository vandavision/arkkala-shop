"""
Service Layer for Shop App.
Handles business logic separated from Views and Models.
"""
from django.db.models import F
from django.contrib.auth import get_user_model
from .models import Product, Comment

User = get_user_model()


class ProductService:
    """Service class for handling product-related business logic."""

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