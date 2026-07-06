"""
Models for managing Payment Transactions.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from orders.models import Order

User = get_user_model()


class Transaction(UUIDBaseModel, TimeStampMixin):
    """Transaction model to track all payment attempts."""
    STATUS_CHOICES = (
        ('pending', _('در انتظار پرداخت')),
        ('successful', _('موفق')),
        ('failed', _('ناموفق')),
        ('canceled', _('لغو شده')),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions', verbose_name=_('کاربر'))
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('سفارش'))
    
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('مبلغ تراکنش'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('وضعیت'))
    gateway = models.CharField(max_length=50, verbose_name=_('درگاه پرداخت'))
    
    authority = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('کد ارجاع اولیه (Authority)'))
    ref_id = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('کد پیگیری نهایی (RefId)'))
    description = models.TextField(null=True, blank=True, verbose_name=_('توضیحات خطا یا رویداد'))

    class Meta:
        verbose_name = _('تراکنش')
        verbose_name_plural = _('تراکنش‌ها')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.gateway} - {self.amount} - {self.get_status_display()}"