import pytest
from blog.repositories.post import PostRepository
from blog.repositories.comment import CommentRepository
from blog.repositories.base import BaseRepository
from blog.models import Post, Category

@pytest.mark.django_db
class TestBlogRepositories:

    def test_base_repository_get_methods(self, category: Category) -> None:
        repo = BaseRepository(Category)
        assert repo.get_by_uuid(category.uuid) == category
        assert repo.get_by_slug(category.slug) == category
        assert repo.get_by_slug("non-existent") is None

    def test_base_repository_save_and_delete(self) -> None:
        repo = BaseRepository(Category)
        new_cat = Category(title="News", slug="news", is_active=True)
        saved_cat = repo.save(new_cat)
        assert saved_cat.uuid is not None

        repo.delete(saved_cat)
        assert repo.get_by_slug("news") is None

    def test_post_repository_increment_view_count(self, post: Post) -> None:
        repo = PostRepository()
        success: bool = repo.increment_view_count(post.slug)
        assert success is True
        post.refresh_from_db()
        assert post.view_count == 1

    def test_comment_repository_initialization(self) -> None:
        repo = CommentRepository()
        assert repo.model.__name__ == "Comment"