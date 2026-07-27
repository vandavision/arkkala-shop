# arkkala/blog/models/comment.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

User = get_user_model()

class Comment(UUIDBaseModel, TimeStampMixin):
    """Comment model for blog posts."""
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments', verbose_name=_('مقاله'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_comments', verbose_name=_('کاربر'))
    body = models.TextField(verbose_name=_('متن نظر'))
    is_approved = models.BooleanField(default=False, verbose_name=_('تایید شده'))

    class Meta:
        verbose_name = _('نظر مقاله')
        verbose_name_plural = _('نظرات مقالات')
        ordering = ['-created_at']
        
    def __str__(self) -> str:
        return f"Comment on {self.post.title}"