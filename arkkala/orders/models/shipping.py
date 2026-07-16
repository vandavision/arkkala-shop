from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin


class ShippingMethod(UUIDBaseModel, TimeStampMixin):
    """Shipping methods like Pishtaz (Paid online) or Tipax (Pay on delivery)."""
    name = models.CharField(max_length=150, verbose_name=_('نام روش ارسال'))
    description = models.TextField(null=True, blank=True, verbose_name=_('توضیحات'))
    base_cost = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_('هزینه پایه'))
    is_pay_on_delivery = models.BooleanField(
        default=False, 
        verbose_name=_('پس کرایه است؟'),
        help_text=_('اگر فعال باشد، هزینه در فاکتور محاسبه نمیشود (مثل تیپاکس).')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('روش ارسال')
        verbose_name_plural = _('روش های ارسال')

    def __str__(self) -> str:
        return self.name