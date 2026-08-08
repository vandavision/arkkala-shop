import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from blog.application.commands.post import PostCommandService
from blog.application.commands.comment import CommentCommandService
from blog.application.queries.post import PostQueryService
from blog.application.queries.category import CategoryQueryService
from blog.application.dtos import CommentCreateDTO
from blog.models import Post, Category, Comment

User = get_user_model()

@pytest.mark.django_db
class TestBlogServices:

    def test_post_command_service_increment_views(self, post: Post) -> None:
        PostCommandService.increment_view_count(post.slug)
        post.refresh_from_db()
        assert post.view_count == 1

    def test_comment_command_service_create(self, post: Post, user: User) -> None:
        dto = CommentCreateDTO(post_slug=post.slug, body="Awesome read", user_id=user.id)
        comment: Comment = CommentCommandService.create_comment(dto)
        assert comment.post == post
        assert comment.user == user
        assert comment.body == "Awesome read"

    def test_comment_command_service_invalid_post(self, user: User) -> None:
        dto = CommentCreateDTO(post_slug="invalid-slug", body="Awesome read", user_id=user.id)
        with pytest.raises(ValueError):
            CommentCommandService.create_comment(dto)

    def test_comment_command_service_invalid_body(self, post: Post) -> None:
        dto = CommentCreateDTO(post_slug=post.slug, body="  ", user_id=None)
        with pytest.raises(ValidationError):
            CommentCommandService.create_comment(dto)

    def test_post_query_service_get_optimized(self, post: Post, comment: Comment) -> None:
        posts = PostQueryService.get_optimized_posts()
        assert posts.count() == 1
        assert hasattr(posts.first(), 'approved_comments')
        assert len(posts.first().approved_comments) == 1

    def test_category_query_service_get_active(self, category: Category) -> None:
        Category.objects.create(title="Inactive", slug="inact", is_active=False)
        categories = CategoryQueryService.get_active_categories()
        assert categories.count() == 1
        assert categories.first() == category