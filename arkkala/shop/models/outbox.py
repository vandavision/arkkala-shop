from django.db import models
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

try:
    from django_jsonform.models.fields import JSONField
except ImportError:
    JSONField = models.JSONField

class OutboxEvent(UUIDBaseModel, TimeStampMixin):
    """Records Domain Events for asynchronous processing (Transactional Outbox Pattern)."""
    event_type = models.CharField(max_length=255, verbose_name='نوع رویداد')
    payload = JSONField(verbose_name='داده‌های رویداد')
    is_processed = models.BooleanField(default=False, verbose_name='پردازش شده')

    class Meta:
        verbose_name = 'رویداد Outbox'
        verbose_name_plural = 'رویدادهای Outbox'
        indexes = [
            models.Index(fields=['is_processed', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} - Processed: {self.is_processed}"