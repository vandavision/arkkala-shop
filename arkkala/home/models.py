"""
Models for Home Page CMS (Stories, Sliders, Banners, Store Reviews).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin


class Story(UUIDBaseModel, TimeStampMixin):
    """
    Instagram-like Stories for the home page supporting images and videos.
    """
    title: str = models.CharField(max_length=100, verbose_name=_('عنوان استوری'))
    image = models.ImageField(upload_to='home/stories/', verbose_name=_('تصویر کاور استوری'))
    video = models.FileField(upload_to='home/stories/videos/', null=True, blank=True, verbose_name=_('ویدیوی استوری'))
    link: str = models.URLField(null=True, blank=True, verbose_name=_('لینک هدایت'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال/نمایش'))

    class Meta:
        verbose_name = _('استوری')
        verbose_name_plural = _('استوری‌ها')
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title


class Slider(UUIDBaseModel, TimeStampMixin):
    """Main Carousel Sliders."""
    title = models.CharField(max_length=255, verbose_name=_('عنوان اسلایدر'))
    image = models.ImageField(upload_to='home/sliders/', verbose_name=_('تصویر اسلایدر'))
    link = models.URLField(null=True, blank=True, verbose_name=_('لینک هدایت'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('اسلایدر')
        verbose_name_plural = _('اسلایدرها')
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Banner(UUIDBaseModel, TimeStampMixin):
    """Promotional Banners placed between sections."""
    title = models.CharField(max_length=255, verbose_name=_('عنوان بنر'))
    image = models.ImageField(upload_to='home/banners/', verbose_name=_('تصویر بنر'))
    link = models.URLField(null=True, blank=True, verbose_name=_('لینک هدایت'))
    position = models.CharField(max_length=50, help_text=_('مثال: top_left, middle_row'), verbose_name=_('موقعیت نمایش'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('بنر تبلیغاتی')
        verbose_name_plural = _('بنرهای تبلیغاتی')

    def __str__(self):
        return f"{self.title} ({self.position})"


class StoreReview(UUIDBaseModel, TimeStampMixin):
    """Static reviews about the store for the homepage footer section."""
    user_name = models.CharField(max_length=150, verbose_name=_('نام کاربر'))
    body = models.TextField(verbose_name=_('متن نظر'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('نظر درباره فروشگاه')
        verbose_name_plural = _('نظرات درباره فروشگاه')
        ordering = ['-created_at']

    def __str__(self):
        return self.user_name