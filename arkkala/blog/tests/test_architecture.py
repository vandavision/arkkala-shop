import pytest
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from blog.models import Post, Comment
from blog.application.commands.post import PostCommandService
from blog.application.commands.comment import CommentCommandService
from blog.application.queries.post import PostQueryService
from blog.application.dtos import CommentCreateDTO

@pytest.mark.django_db
class TestBlogEnterpriseArchitecture:

    def test_post_atomic_concurrency_increment(self, post: Post) -> None:
        initial_views: int = post.view_count
        PostCommandService.increment_view_count(post.slug)
        post.refresh_from_db()
        assert post.view_count == initial_views + 1

    @patch('blog.signals.cache.delete_pattern', create=True)
    def test_cache_invalidation_signals(self, mock_delete_pattern, post: Post) -> None:
        PostQueryService.cache_strategy.get_or_set("list", lambda: 100)
        assert PostQueryService.cache_strategy.get("list") == 100
        
        post.title = "Updated Title"
        post.save()
        
        assert PostQueryService.cache_strategy.get("list") is None

    def test_comment_strict_creation_dto(self, post: Post) -> None:
        dto = CommentCreateDTO(post_slug=post.slug, body="  ", user_id=None)
        with pytest.raises(ValidationError):
            CommentCommandService.create_comment(dto)

    def test_queryset_isolation_comments(self, post: Post) -> None:
        Comment.objects.create(post=post, body="Hidden spam message", is_approved=False)
        posts = PostQueryService.get_optimized_posts()
        extracted_post = posts.first()
        assert extracted_post is not None
        assert len(extracted_post.approved_comments) == 0

    def test_api_view_count_side_effect(self, api_client: APIClient, post: Post) -> None:
        url: str = reverse('post-detail', kwargs={'slug': post.slug})
        initial: int = post.view_count
        res = api_client.get(url)
        assert res.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.view_count == initial + 1