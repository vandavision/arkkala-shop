import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import Product

@pytest.mark.django_db
class TestAPIControllers:
    """Proves framework integration routes errors seamlessly via decoractors."""

    def test_add_comment_bad_request(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('product-add-comment', kwargs={'slug': product.slug})
        payload = {'body': 'a', 'rating': 10} 
        response = api_client.post(url, data=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_product_not_found(self, api_client: APIClient) -> None:
        url: str = reverse('product-detail', kwargs={'slug': 'non-existing'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_max_price_api(self, api_client: APIClient, product: Product) -> None:
        url: str = reverse('max-price')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK