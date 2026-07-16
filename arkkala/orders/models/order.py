from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from platform_tools.mixins.models.address import AddressMixin
from shop.models import Product, ProductVariant

from .shipping import ShippingMethod
from .coupon import Coupon

User = get_user_model()


class Order(UUIDBaseModel, TimeStampMixin, AddressMixin):
    """Finalized Order combining User, Address, Shipping, and Costs."""
    STATUS_CHOICES = (
        ('pending', _('در انتظار پرداخت')), ('paid', _('پرداخت شده')),
        ('processing', _('در حال پردازش')), ('shipped', _('ارسال شده')),
        ('delivered', _('تحویل داده شده')), ('cancelled', _('لغو شده')),
        ('returned', _('مرجوع شده')),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True, verbose_name=_('کاربر'))
    
    guest_first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('نام مهمان'))
    guest_last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('نام خانوادگی مهمان'))
    guest_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('موبایل مهمان'))
    
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


class OrderRequest(UUIDBaseModel, TimeStampMixin):
    """Handles requests for cancelling or returning an order."""
    class RequestTypeChoices(models.TextChoices):
        CANCEL = 'cancel', _('لغو سفارش')
        RETURN = 'return', _('مرجوعی کالا')

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('در انتظار بررسی')
        APPROVED = 'approved', _('تایید شده')
        REJECTED = 'rejected', _('رد شده')

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='action_request', verbose_name=_('سفارش'))
    request_type = models.CharField(max_length=20, choices=RequestTypeChoices.choices, verbose_name=_('نوع درخواست'))
    reason = models.TextField(verbose_name=_('دلیل درخواست'))
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name=_('وضعیت'))
    admin_note = models.TextField(blank=True, null=True, verbose_name=_('توضیحات ادمین'))

    class Meta:
        verbose_name = _('درخواست لغو/مرجوعی')
        verbose_name_plural = _('درخواست‌های لغو و مرجوعی')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"درخواست {self.get_request_type_display()} برای سفارش {self.order.pk}"