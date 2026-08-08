import pytest
from typing import Generator
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from blog.models import Category, Tag, Post, Comment

User = get_user_model()

@pytest.fixture(autouse=True)
def clear_cache() -> Generator:
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture
def auth_client(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def user() -> User:
    return User.objects.create_user(
        username='blogtestuser',
        email='blogtest@arkkala.com',
        password='testpassword123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def category() -> Category:
    return Category.objects.create(title='Tech', slug='tech', is_active=True)

@pytest.fixture
def tag() -> Tag:
    return Tag.objects.create(title='Django', slug='django')

@pytest.fixture
def post(category: Category, user: User) -> Post:
    return Post.objects.create(
        author=user,
        category=category,
        title='CQRS Magic',
        slug='cqrs-magic',
        short_description='Short',
        body='Long body explaining CQRS completely.',
        view_count=0,
        read_time=5,
        is_published=True
    )

@pytest.fixture
def comment(post: Post, user: User) -> Comment:
    return Comment.objects.create(
        post=post,
        user=user,
        body='Great architectural insight.',
        is_approved=True
    )