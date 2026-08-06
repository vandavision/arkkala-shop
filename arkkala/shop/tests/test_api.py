import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import Product, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestProductAPI:
    """
    Integration tests for Product API endpoints.
    """

    def test_list_products(self, api_client: APIClient, product: Product) -> None:
        """
        Tests the paginated product listing endpoint.
        """
        url: str = reverse('product-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) >= 1
        assert response.data['results'][0]['title'] == product.title

    def test_retrieve_product(self, api_client: APIClient, product: Product) -> None:
        """
        Tests the product detail endpoint and view count side effect.
        """
        url: str = reverse('product-detail', kwargs={'slug': product.slug})
        initial_views: int = product.view_count
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == product.title
        
        product.refresh_from_db()
        assert product.view_count == initial_views + 1

    def test_toggle_favorite_authenticated(self, auth_client: APIClient, product: Product) -> None:
        """
        Tests the favorite toggling endpoint with authentication.
        """
        url: str = reverse('product-toggle-favorite', kwargs={'slug': product.slug})
        
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_favorite'] is True

        response = auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_favorite'] is False

    def test_toggle_favorite_unauthenticated(self, api_client: APIClient, product: Product) -> None:
        """
        Ensures unauthenticated users cannot toggle favorites.
        """
        url: str = reverse('product-toggle-favorite', kwargs={'slug': product.slug})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_comment(self, api_client: APIClient, product: Product) -> None:
        """
        Tests the endpoint for submitting a product comment.
        """
        url: str = reverse('product-add-comment', kwargs={'slug': product.slug})
        payload: dict[str, Any] = {
            'body': 'This is a test comment.',
            'rating': 4
        }
        
        response = api_client.post(url, data=payload)
        assert response.status_code == status.HTTP_201_CREATED
        
        comment_exists: bool = Comment.objects.filter(product=product, body='This is a test comment.').exists()
        assert comment_exists is True

    def test_add_question(self, api_client: APIClient, product: Product) -> None:
        """
        Tests the endpoint for submitting a product question.
        """
        url: str = reverse('product-add-question', kwargs={'slug': product.slug})
        payload: dict[str, str] = {
            'text': 'What is the material?',
            'name': 'Alice'
        }
        
        response = api_client.post(url, data=payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_max_price_api(self, api_client: APIClient, product: Product) -> None:
        """
        Tests the maximum price retrieval endpoint.
        """
        url: str = reverse('max-price')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'max_price' in response.data
        assert response.data['max_price'] >= product.base_price


@pytest.mark.django_db
class TestCommentAPI:
    """
    Integration tests for Comment API endpoints.
    """

    def test_my_comments_authenticated(self, auth_client: APIClient, comment: Comment) -> None:
        """
        Tests the retrieval of a user's own comments.
        """
        url: str = reverse('comment-my-comments')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['body'] == comment.body

    def test_my_comments_unauthenticated(self, api_client: APIClient) -> None:
        """
        Ensures unauthenticated users cannot retrieve personal comments.
        """
        url: str = reverse('comment-my-comments')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED