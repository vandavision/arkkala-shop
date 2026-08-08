from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

User = get_user_model()

class Comment(UUIDBaseModel, TimeStampMixin):
    """
    Comment entity for blog posts representing user feedback and strict validation.
    """
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='comments', verbose_name=_('مقاله'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_comments', verbose_name=_('کاربر'))
    body = models.TextField(verbose_name=_('متن نظر'), validators=[MinLengthValidator(5)])
    is_approved = models.BooleanField(default=False, verbose_name=_('تایید شده'))

    class Meta:
        verbose_name: str = _('نظر مقاله')
        verbose_name_plural: str = _('نظرات مقالات')
        ordering: list = ['-created_at']
        indexes: list = [
            models.Index(fields=['post', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
        ]
        
    def __str__(self) -> str:
        """
        Returns the string representation of the Comment.
        """
        return f"Comment on {self.post.title}"