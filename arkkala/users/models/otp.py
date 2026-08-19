import uuid
from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from platform_tools.mixins.models.base import TimeStampMixin

class OTPRequest(TimeStampMixin):
    """
    Logs temporary access code requests controlling authentication throughput.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    identifier = models.CharField(max_length=255, verbose_name=_('شناسه (تلفن/ایمیل)'))
    code = models.CharField(max_length=6, verbose_name=_('کد تایید'))
    ip_address = models.GenericIPAddressField(verbose_name=_('آدرس IP'))
    is_used = models.BooleanField(default=False, verbose_name=_('استفاده شده؟'))
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('درخواست کد یکبار مصرف')
        verbose_name_plural = _('درخواست‌های کدهای یکبار مصرف')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['identifier', 'is_used', 'expires_at']),
        ]

    def clean(self) -> None:
        super().clean()
        if not self.expires_at:
            wait_time: int = getattr(settings, 'OTP_WAIT_TIME_MINUTES', 2)
            self.expires_at = timezone.now() + timedelta(minutes=wait_time)

    def __str__(self) -> str:
        return f"{self.identifier} - {self.code}"