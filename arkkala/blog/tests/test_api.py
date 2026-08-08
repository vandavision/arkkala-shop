import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from blog.models import Post, Category

@pytest.mark.django_db
class TestBlogAPI:

    def test_list_categories(self, api_client: APIClient, category: Category) -> None:
        url: str = reverse('blog-category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['slug'] == category.slug

    def test_list_posts(self, api_client: APIClient, post: Post) -> None:
        url: str = reverse('post-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['slug'] == post.slug

    def test_retrieve_post(self, api_client: APIClient, post: Post) -> None:
        url: str = reverse('post-detail', kwargs={'slug': post.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['slug'] == post.slug
        assert 'body' in response.data

    def test_add_comment_authenticated(self, auth_client: APIClient, post: Post) -> None:
        url: str = reverse('post-add-comment', kwargs={'slug': post.slug})
        data: dict = {'body': 'Excellent tutorial.'}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "موفقیت" in response.data['message']

    def test_add_comment_unauthenticated(self, api_client: APIClient, post: Post) -> None:
        url: str = reverse('post-add-comment', kwargs={'slug': post.slug})
        data: dict = {'body': 'Anonymous feedback.'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "موفقیت" in response.data['message']

    def test_add_comment_invalid_payload(self, api_client: APIClient, post: Post) -> None:
        url: str = reverse('post-add-comment', kwargs={'slug': post.slug})
        data: dict = {'body': ''}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_comment_invalid_post_slug(self, api_client: APIClient) -> None:
        url: str = reverse('post-add-comment', kwargs={'slug': 'non-existent'})
        data: dict = {'body': 'This should fail.'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND