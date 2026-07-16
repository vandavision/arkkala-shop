from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin


class Coupon(UUIDBaseModel, TimeStampMixin):
    """Discount Codes Configuration."""
    code = models.CharField(max_length=50, unique=True, verbose_name=_('کد تخفیف'))
    discount_percent = models.PositiveIntegerField(default=0, verbose_name=_('درصد تخفیف'))
    max_discount_amount = models.DecimalField(
        max_digits=12, decimal_places=0, null=True, blank=True, verbose_name=_('سقف مبلغ تخفیف')
    )
    valid_from = models.DateTimeField(verbose_name=_('معتبر از'))
    valid_to = models.DateTimeField(verbose_name=_('معتبر تا'))
    usage_limit = models.PositiveIntegerField(default=1, verbose_name=_('محدودیت تعداد استفاده'))
    used_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد استفاده شده'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('کد تخفیف')
        verbose_name_plural = _('کدهای تخفیف')

    def __str__(self) -> str:
        return self.code