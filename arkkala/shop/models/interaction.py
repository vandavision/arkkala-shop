from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from .product import Product

User = get_user_model()

class Comment(UUIDBaseModel, TimeStampMixin):
    """Product Comments and Ratings with strict input validation."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name='محصول')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')
    body = models.TextField(verbose_name='متن نظر', validators=[MinLengthValidator(2)])
    rating = models.PositiveSmallIntegerField(
        default=5, 
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        verbose_name='امتیاز'
    )
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده')

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
        ]

class Question(UUIDBaseModel, TimeStampMixin):
    """Product Questions mapping."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions', verbose_name='محصول')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر ثبت‌نام شده')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام نویسنده مهمان')
    text = models.TextField(verbose_name='متن پرسش', validators=[MinLengthValidator(5)])
    answer_text = models.TextField(null=True, blank=True, verbose_name='متن پاسخ ادمین')
    is_approved = models.BooleanField(default=False, verbose_name='تایید شده برای نمایش')

    class Meta:
        verbose_name = 'پرسش و پاسخ'
        verbose_name_plural = 'پرسش‌ها و پاسخ‌ها'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['product', 'is_approved'])]
        
    def __str__(self) -> str:
        author = self.user.get_full_name() if self.user else (self.name or 'کاربر مهمان')
        return f"Question on {self.product.title} by {author}"

class UserProductHistory(UUIDBaseModel, TimeStampMixin):
    """Tracks user and guest product view history for the recommendation engine."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_view_history', null=True, blank=True, verbose_name='کاربر')
    guest_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='شناسه مهمان')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_views', verbose_name='محصول')
    view_count = models.PositiveIntegerField(default=1, verbose_name='دفعات بازدید')

    class Meta:
        verbose_name = 'تاریخچه بازدید کاربر'
        verbose_name_plural = 'تاریخچه بازدید کاربران'
        ordering = ['-modified_at']
        indexes = [
            models.Index(fields=['user', '-modified_at']),
            models.Index(fields=['guest_id', '-modified_at']),
        ]

    def __str__(self) -> str:
        identifier = self.user.get_full_name() if self.user else f"Guest ({self.guest_id})"
        return f"{identifier} viewed {self.product.title}"