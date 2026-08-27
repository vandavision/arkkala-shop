from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

class FAQ(UUIDBaseModel, TimeStampMixin):
    """
    Model for managing Frequently Asked Questions (FAQs).
    """
    question: str = models.CharField(max_length=255, verbose_name=_('پرسش'))
    answer: str = models.TextField(verbose_name=_('پاسخ'))
    order: int = models.PositiveIntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name: str = _('سوال متداول')
        verbose_name_plural: str = _('سوالات متداول')
        ordering: list[str] = ['order', '-created_at']

    def __str__(self) -> str:
        return str(self.question)