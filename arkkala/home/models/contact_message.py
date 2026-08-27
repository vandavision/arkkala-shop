from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

class ContactMessage(UUIDBaseModel, TimeStampMixin):
    """
    Model for persisting inbound contact requests.
    """
    full_name: str = models.CharField(max_length=150, verbose_name=_('نام و نام خانوادگی'))
    phone_number: str = models.CharField(max_length=20, verbose_name=_('شماره تماس'))
    email: str = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_('پست الکترونیک'))
    subject: str = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('موضوع پیام'))
    message: str = models.TextField(verbose_name=_('متن پیام'))
    is_read: bool = models.BooleanField(default=False, verbose_name=_('خوانده شده'))

    class Meta:
        verbose_name: str = _('پیام تماس با ما')
        verbose_name_plural: str = _('پیام‌های تماس با ما')
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return f"{self.full_name} - {self.subject or 'بدون موضوع'}"