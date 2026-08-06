import pytest
from typing import Generator
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from shop.models import (
    Category, Brand, Attribute, AttributeValue, 
    Product, ProductVariant, Comment, Question
)

User = get_user_model()

@pytest.fixture(autouse=True)
def clear_cache() -> Generator:
    """
    Clears Django cache before each test to ensure test isolation.
    """
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def api_client() -> APIClient:
    """
    Provides an unauthenticated API client.
    """
    return APIClient()

@pytest.fixture
def auth_client(user: User) -> APIClient:
    """
    Provides an authenticated API client.
    """
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def user() -> User:
    """
    Creates a standard test user.
    """
    return User.objects.create_user(
        email='testuser@arkkala.com',
        password='testpassword123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def category() -> Category:
    """
    Creates a base product category.
    """
    return Category.objects.create(title='Test Category', slug='test-category')

@pytest.fixture
def brand() -> Brand:
    """
    Creates a base product brand.
    """
    return Brand.objects.create(title='Test Brand', slug='test-brand')

@pytest.fixture
def attribute() -> Attribute:
    """
    Creates a generic attribute key.
    """
    return Attribute.objects.create(title='Color', slug='color')

@pytest.fixture
def attribute_value(attribute: Attribute) -> AttributeValue:
    """
    Creates a value for a specific attribute.
    """
    return AttributeValue.objects.create(attribute=attribute, value='Red')

@pytest.fixture
def product(category: Category, brand: Brand) -> Product:
    """
    Creates a fully populated active product.
    """
    return Product.objects.create(
        title='Test Product',
        english_title='Test Product EN',
        slug='test-product',
        category=category,
        brand=brand,
        description='A complete description of the test product.',
        base_price=100000,
        base_inventory=50,
        is_active=True
    )

@pytest.fixture
def product_variant(product: Product, attribute_value: AttributeValue) -> ProductVariant:
    """
    Creates a variant attached to a product.
    """
    variant = ProductVariant.objects.create(
        product=product,
        price=105000,
        inventory=10
    )
    variant.attribute_values.add(attribute_value)
    return variant

@pytest.fixture
def comment(product: Product, user: User) -> Comment:
    """
    Creates an approved comment.
    """
    return Comment.objects.create(
        product=product,
        user=user,
        body='Great product!',
        rating=5,
        is_approved=True
    )

@pytest.fixture
def question(product: Product, user: User) -> Question:
    """
    Creates an approved question.
    """
    return Question.objects.create(
        product=product,
        user=user,
        text='Is this available in blue?',
        answer_text='Not currently.',
        is_approved=True
    )