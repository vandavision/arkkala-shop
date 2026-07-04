"""
Models for Orders, Cart, Coupons, and Shipping Methods.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from platform_tools.mixins.models.address import AddressMixin
from shop.models import Product, ProductVariant

User = get_user_model()


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


class Coupon(UUIDBaseModel, TimeStampMixin):
    """Discount Codes."""
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


class Cart(UUIDBaseModel, TimeStampMixin):
    """User Shopping Cart."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name=_('کاربر'))

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


class Order(UUIDBaseModel, TimeStampMixin, AddressMixin):
    """Finalized Order combining User, Address, Shipping, and Costs."""
    STATUS_CHOICES = (
        ('pending', _('در انتظار پرداخت')),
        ('paid', _('پرداخت شده')),
        ('processing', _('در حال پردازش')),
        ('shipped', _('ارسال شده')),
        ('delivered', _('تحویل داده شده')),
        ('cancelled', _('لغو شده')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('کاربر'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('وضعیت سفارش'))
    
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True, verbose_name=_('روش ارسال'))
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('کد تخفیف'))
    
    total_items_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_('مبلغ کل کالاها'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_('مبلغ تخفیف'))
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_('هزینه ارسال'))
    payable_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_('مبلغ قابل پرداخت'))
    
    tracking_code = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('کد رهگیری پستی'))
    is_paid = models.BooleanField(default=False, verbose_name=_('پرداخت شده؟'))

    class Meta:
        verbose_name = _('سفارش')
        verbose_name_plural = _('سفارشات')
        ordering = ['-created_at']


class OrderItem(UUIDBaseModel, TimeStampMixin):
    """Snapshot of purchased products."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('سفارش'))
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name=_('محصول'))
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('تنوع'))
    
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('تعداد'))
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('قیمت واحد (در زمان خرید)'))
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('قیمت کل این سطر'))

    class Meta:
        verbose_name = _('آیتم سفارش')
        verbose_name_plural = _('آیتم های سفارش')