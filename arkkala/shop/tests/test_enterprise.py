import pytest
from typing import Any, Dict
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from shop.models import Product, Comment, Category, Brand
from shop.application.commands.product import ProductCommandService
from shop.application.queries.product import ProductQueryService

User = get_user_model()

@pytest.fixture
def test_category() -> Category:
    return Category.objects.create(title="Test Category", slug="test-cat")

@pytest.fixture
def test_brand() -> Brand:
    return Brand.objects.create(title="Test Brand", slug="test-brand")

@pytest.fixture
def test_product(test_category: Category, test_brand: Brand) -> Product:
    return Product.objects.create(
        title="Test Product",
        slug="test-prod",
        category=test_category,
        brand=test_brand,
        description="A cool product",
        base_price=1000,
        is_active=True
    )

@pytest.fixture
def test_user() -> User:
    return User.objects.create_user(email="test@arkkala.com", password="password123")

@pytest.mark.django_db
class TestSeniorGradeQuality:
    """
    Tests focused on Validation, Authorization Isolation, Concurrency concepts, and Caching.
    """

    def test_product_wholesale_validation_enforcement(self) -> None:
        """
        Validates business logic constraints strictly run at the model level via clean().
        """
        product = Product(
            title="Wholesale Bad Product", slug="bad", description="Desc",
            base_price=1000, is_wholesale=True, 
            wholesale_min_quantity=1, wholesale_base_price=1500
        )
        with pytest.raises(ValidationError) as exc:
            product.clean()
            
        assert "حداقل تعداد" in str(exc.value)
        
        product.wholesale_min_quantity = 5
        with pytest.raises(ValidationError) as exc:
            product.clean()
            
        assert "کمتر از قیمت پایه" in str(exc.value)

    def test_comment_rating_validation(self, test_user: User, test_product: Product) -> None:
        """
        Validates rating boundary limits.
        """
        comment = Comment(product=test_product, user=test_user, body="Test", rating=6)
        with pytest.raises(ValidationError):
            comment.full_clean()

    def test_atomic_view_count_increment(self, test_product: Product) -> None:
        """
        Validates the atomic increment repository bypasses ORM object states.
        """
        initial_views: int = test_product.view_count
        ProductCommandService.increment_view_count(test_product.slug)
        test_product.refresh_from_db()
        assert test_product.view_count == initial_views + 1

    def test_comment_data_leak_secured(self, test_user: User, test_product: Product) -> None:
        """
        Ensures User A cannot view User B's comments via the Dashboard API.
        """
        user2 = User.objects.create_user(email='other@arkkala.com', password='pwd')
        Comment.objects.create(product=test_product, user=user2, body='User 2 Secret Comment', rating=5)

        client = APIClient()
        client.force_authenticate(user=test_user)
        
        url: str = reverse('comment-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Must return empty results since 'test_user' hasn't posted anything
        assert len(response.data['results']) == 0

    def test_max_price_cache_invalidation_sync(self, test_product: Product) -> None:
        """
        Validates that changing a product actively drops the correct cache key.
        """
        # Will cache 1000
        cached_price: int = ProductQueryService.get_max_price()
        assert cached_price == 1000
        
        # New product updates max, triggers signal
        Product.objects.create(title="Max Prod", slug="max", description="Max", base_price=5000, is_active=True)
        
        # Fetching again should query DB, not return stale cache
        new_cached_price: int = ProductQueryService.get_max_price()
        assert new_cached_price == 5000