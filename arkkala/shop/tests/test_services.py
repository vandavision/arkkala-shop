import pytest
from typing import Dict, Any
from shop.models import Product, Comment, Question
from shop.services import ProductService, InteractionService
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestProductService:
    """
    Unit tests for Product Service business logic.
    """

    def test_get_max_price(self, product: Product, category: Any, brand: Any) -> None:
        """
        Validates maximum price aggregation and caching.
        """
        Product.objects.create(
            title='Expensive Product',
            slug='expensive-product',
            category=category,
            brand=brand,
            description='Expensive',
            base_price=500000,
            is_active=True
        )

        max_price: int = ProductService.get_max_price()
        assert max_price == 500000

        ProductService.invalidate_product_caches()
        cached_max = ProductService.get_max_price()
        assert cached_max == 500000

    def test_increment_view_count(self, product: Product) -> None:
        """
        Validates the atomic incrementation of product view counts.
        """
        initial_views: int = product.view_count
        ProductService.increment_view_count(product)
        
        assert product.view_count == initial_views + 1

    def test_toggle_favorite_add(self, product: Product, user: User) -> None:
        """
        Validates adding a product to user favorites.
        """
        result: Dict[str, Any] = ProductService.toggle_favorite(product, user)
        
        assert result["is_favorite"] is True
        assert product.favorites.filter(id=user.id).exists()

    def test_toggle_favorite_remove(self, product: Product, user: User) -> None:
        """
        Validates removing a product from user favorites.
        """
        product.favorites.add(user)
        result: Dict[str, Any] = ProductService.toggle_favorite(product, user)
        
        assert result["is_favorite"] is False
        assert not product.favorites.filter(id=user.id).exists()


@pytest.mark.django_db
class TestInteractionService:
    """
    Unit tests for Interaction Service business logic.
    """

    def test_add_comment(self, product: Product, user: User) -> None:
        """
        Validates comment creation logic.
        """
        comment: Comment = InteractionService.add_comment(
            product=product,
            user=user,
            body="Nice quality.",
            rating=4
        )
        
        assert comment.product == product
        assert comment.user == user
        assert comment.rating == 4
        assert comment.is_approved is False

    def test_add_question_authenticated(self, product: Product, user: User) -> None:
        """
        Validates question creation logic for authenticated users.
        """
        question: Question = InteractionService.add_question(
            product=product,
            text="Does it have warranty?",
            user=user
        )
        
        assert question.product == product
        assert question.user == user
        assert question.name is None

    def test_add_question_guest(self, product: Product) -> None:
        """
        Validates question creation logic for guest users.
        """
        question: Question = InteractionService.add_question(
            product=product,
            text="How long is shipping?",
            name="John Doe"
        )
        
        assert question.product == product
        assert question.user is None
        assert question.name == "John Doe"