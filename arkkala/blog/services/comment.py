# arkkala/blog/services/comment.py
from typing import Optional
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from blog.models.post import Post
from blog.models.comment import Comment

class CommentService:
    """Service layer for Comment business logic."""

    @staticmethod
    def create_comment(post: Post, body: str, user: Optional[AbstractBaseUser] = None) -> Comment:
        """Creates a new comment for a given post."""
        if not body or not body.strip():
            raise ValidationError("متن نظر نمی‌تواند خالی باشد.")

        return Comment.objects.create(
            post=post,
            user=user,
            body=body.strip()
        )