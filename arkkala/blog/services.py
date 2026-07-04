"""
Service Layer for Blog App.
Handles business logic separated from Views and Models.
"""
from django.db.models import F
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class PostService:
    """Service class for handling post-related business logic."""

    @staticmethod
    def increment_view_count(post: Post) -> None:
        """
        Increments the view count of a post atomically.
        
        Args:
            post (Post): The post instance to update.
        """
        Post.objects.filter(pk=post.pk).update(view_count=F('view_count') + 1)
        post.refresh_from_db(fields=['view_count'])

    @staticmethod
    def add_comment(post: Post, user: User | None, body: str) -> Comment:
        """
        Adds a new comment to a post.
        
        Args:
            post (Post): The post to comment on.
            user (User | None): The user submitting the comment (or None for anonymous).
            body (str): The comment text.
            
        Returns:
            Comment: The newly created comment instance.
        """
        return Comment.objects.create(
            post=post,
            user=user,
            body=body
        )