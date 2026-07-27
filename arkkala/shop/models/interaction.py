# shop/models/interaction.py
from django.db import models
from django.contrib.auth import get_user_model
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from .product import Product

User = get_user_model()


class Comment(UUIDBaseModel, TimeStampMixin):
    """Product Comments & Ratings."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name='محصول')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')
    body = models.TextField(verbose_name='متن نظر')
    rating = models.PositiveSmallIntegerField(default=5, verbose_name='امتیاز')
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده')

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'


class Question(UUIDBaseModel, TimeStampMixin):
    """Represents a user or guest question for AEO."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions', verbose_name='محصول')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر ثبت‌نام شده')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام نویسنده مهمان')
    text = models.TextField(verbose_name='متن پرسش')
    answer_text = models.TextField(null=True, blank=True, verbose_name='متن پاسخ ادمین')
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده برای نمایش')

    class Meta:
        verbose_name = 'پرسش و پاسخ'
        verbose_name_plural = 'پرسش‌ها و پاسخ‌ها'
        ordering = ['-created_at']

    def __str__(self) -> str:
        author = self.user.get_full_name() if self.user else (self.name or 'کاربر مهمان')
        return f"Question on {self.product.title} by {author}"