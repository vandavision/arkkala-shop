"""
Models for Shipping, Cart, and Orders with Guest Checkout support.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from platform_tools.mixins.models.address import AddressMixin
from shop.models import ProductVariant


class ShippingMethod(UUIDBaseModel, TimeStampMixin):
    """Available Shipping Methods (e.g., Post, Tipax)."""
    title = models.CharField(max_length=100, verbose_name=_('عنوان روش ارسال'))
    description = models.TextField(null=True, blank=True, verbose_name=_('توضیحات'))
    base_cost = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name=_('هزینه پایه (تومان)'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('روش ارسال')
        verbose_name_plural = _('روش‌های ارسال')

    def __str__(self) -> str:
        return self.title


class Cart(UUIDBaseModel, TimeStampMixin):
    """Shopping Cart supporting both Authenticated Users and Guests."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart',
        verbose_name=_('کاربر')
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('شناسه جلسه (مهمان)')
    )

    class Meta:
        verbose_name = _('سبد خرید')
        verbose_name_plural = _('سبدهای خرید')


class CartItem(UUIDBaseModel, TimeStampMixin):
    """Items inside the Shopping Cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, verbose_name=_('تنوع محصول'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('تعداد'))

    class Meta:
        verbose_name = _('آیتم سبد خرید')
        verbose_name_plural = _('آیتم‌های سبد خرید')
        unique_together = ('cart', 'variant')


class OrderStatus(models.TextChoices):
    PENDING = 'pending', _('در انتظار پرداخت')
    PAID = 'paid', _('پرداخت شده')
    PROCESSING = 'processing', _('در حال پردازش')
    SHIPPED = 'shipped', _('ارسال شده')
    DELIVERED = 'delivered', _('تحویل داده شده')
    CANCELED = 'canceled', _('لغو شده')


class Order(UUIDBaseModel, TimeStampMixin, AddressMixin):
    """Order Model supporting Guest Data and Shipping Costs."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('کاربر')
    )
    # Guest Information Fields
    guest_mobile = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('موبایل مهمان'))
    guest_first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('نام مهمان'))
    guest_last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('نام خانوادگی مهمان'))

    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('روش ارسال')
    )
    
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name=_('وضعیت')
    )
    
    products_total = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('مجموع مبلغ کالاها'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name=_('هزینه ارسال'))
    payable_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('مبلغ نهایی قابل پرداخت'))

    class Meta:
        verbose_name = _('سفارش')
        verbose_name_plural = _('سفارشات')


class OrderItem(UUIDBaseModel, TimeStampMixin):
    """Items inside an Order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, verbose_name=_('تنوع محصول'))
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('قیمت در زمان ثبت'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('تعداد'))

    class Meta:
        verbose_name = _('آیتم سفارش')
        verbose_name_plural = _('آیتم‌های سفارش')