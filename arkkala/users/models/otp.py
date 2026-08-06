import uuid
from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class OTPRequest(models.Model):
    """
    Tracks all OTP requests for rate limiting and spam prevention.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    identifier = models.CharField(max_length=255, verbose_name=_('شناسه (تلفن/ایمیل)'))
    code = models.CharField(max_length=6, verbose_name=_('کد تایید'))
    ip_address = models.GenericIPAddressField(verbose_name=_('آدرس IP'))
    is_used = models.BooleanField(default=False, verbose_name=_('استفاده شده؟'))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('درخواست کد یکبار مصرف')
        verbose_name_plural = _('درخواست‌های کدهای یکبار مصرف')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['identifier', 'is_used', 'expires_at']),
        ]

    def clean(self) -> None:
        """
        Ensures expiration time is set automatically based on settings.
        """
        super().clean()
        if not self.expires_at:
            wait_time: int = getattr(settings, 'OTP_WAIT_TIME_MINUTES', 2)
            self.expires_at = timezone.now() + timedelta(minutes=wait_time)

    def __str__(self) -> str:
        """
        Returns string representation of OTP Request.
        """
        return f"{self.identifier} - {self.code}"