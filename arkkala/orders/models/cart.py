from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from shop.models import Product, ProductVariant

User = get_user_model()


class Cart(UUIDBaseModel, TimeStampMixin):
    """User and Guest Shopping Cart."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True, verbose_name=_('کاربر'))
    guest_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('شناسه مهمان'))

    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')


class CartItem(UUIDBaseModel, TimeStampMixin):
    """Items inside the Cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('سبد خرید'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('محصول'))
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('تنوع'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('تعداد'))

    class Meta:
        verbose_name = _('آیتم سبد خرید')
        verbose_name_plural = _('آیتم های سبد خرید')