import pytest
from typing import Any
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import Product, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestProductAPI:

    def test_list_products(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_retrieve_product_by_slug(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-detail', kwargs={'slug': product.slug})
        initial_views: int = product.view_count
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.view_count == initial_views + 1

    def test_retrieve_product_by_uuid(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-detail', kwargs={'slug': str(product.uuid)})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_toggle_favorite_authenticated(self, auth_client: APIClient, product: Product) -> None:
        url: str = reverse('product-toggle-favorite', kwargs={'slug': product.slug})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_favorite'] is True

        response = auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_favorite'] is False

    def test_toggle_favorite_not_found(self, auth_client: APIClient) -> None:
        url: str = reverse('product-toggle-favorite', kwargs={'slug': 'non-existent'})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_toggle_favorite_unauthenticated(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-toggle-favorite', kwargs={'slug': product.slug})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_comment(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-add-comment', kwargs={'slug': product.slug})
        payload: dict[str, Any] = {'body': 'This is a test comment.', 'rating': 4}
        response = api_client.post(url, data=payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_add_comment_bad_request(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-add-comment', kwargs={'slug': product.slug})
        payload: dict[str, Any] = {'body': 'a', 'rating': 10}  # Rating invalid
        response = api_client.post(url, data=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_question(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-add-question', kwargs={'slug': product.slug})
        payload: dict[str, str] = {'text': 'What is the material?', 'name': 'Alice'}
        response = api_client.post(url, data=payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_add_question_bad_request(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-add-question', kwargs={'slug': product.slug})
        payload: dict[str, str] = {'text': 'a', 'name': 'A'}  # Very short length
        response = api_client.post(url, data=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_max_price_api(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('max-price')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestCommentAPI:

    def test_my_comments_authenticated(self, auth_client: APIClient, comment: Comment) -> None:
        url: str = reverse('comment-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_my_comments_unpaginated(self, auth_client: APIClient, comment: Comment) -> None:
        url: str = reverse('comment-list')
        with patch('shop.views.interaction.PageNumberPagination.paginate_queryset', return_value=None):
            response = auth_client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.data, list)

    def test_my_comments_unauthenticated(self, api_client: APIClient) -> None:
        url: str = reverse('comment-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED