# arkkala/blog/services/post.py
from django.db.models import F
from blog.models.post import Post

class PostService:
    """Service layer for Post business logic."""

    @staticmethod
    def increment_view_count(post: Post) -> None:
        """Increments the view count of a post atomically."""
        Post.objects.filter(pk=post.pk).update(view_count=F('view_count') + 1)