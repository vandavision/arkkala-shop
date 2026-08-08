from typing import Optional
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from blog.models.post import Post
from blog.models.comment import Comment

class CommentService:
    """
    Service layer for Comment business logic.
    """
    @staticmethod
    def create_comment(post: Post, body: str, user: Optional[AbstractBaseUser] = None) -> Comment:
        """
        Creates and strictly validates a new comment for a given post.
        """
        if not body or not body.strip():
            raise ValidationError("متن نظر نمی‌تواند خالی باشد.")

        comment = Comment(
            post=post,
            user=user,
            body=body.strip()
        )
        comment.full_clean()
        comment.save()
        return comment