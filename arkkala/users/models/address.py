from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from platform_tools.mixins.models.address import AddressMixin

class UserAddress(UUIDBaseModel, TimeStampMixin, AddressMixin):
    """
    Enterprise Address entity mapped to a User.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses', verbose_name=_('کاربر'))
    title = models.CharField(max_length=100, verbose_name=_('عنوان آدرس'), help_text=_('مثال: خانه، محل کار'))
    recipient_first_name = models.CharField(max_length=150, verbose_name=_('نام تحویل گیرنده'))
    recipient_last_name = models.CharField(max_length=150, verbose_name=_('نام خانوادگی تحویل گیرنده'))
    recipient_phone = models.CharField(max_length=20, verbose_name=_('شماره تماس تحویل گیرنده'))
    is_default = models.BooleanField(default=False, verbose_name=_('آدرس پیش‌فرض'))

    class Meta:
        verbose_name = _('آدرس کاربر')
        verbose_name_plural = _('آدرس‌های کاربران')
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
        ]

    def clean(self) -> None:
        """
        Validates the Address object strictly enforcing field requirements.
        """
        super().clean()
        if not self.country:
            self.country = "ایران" # Default value or fetch from settings

    def __str__(self) -> str:
        """
        Returns string representation of the Address.
        """
        return f"{self.title} - {self.user}"