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


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=255, default="ارک کالا", verbose_name="نام سایت")
    logo = models.ImageField(upload_to="site/logo/", null=True, blank=True, verbose_name="لوگوی اصلی")
    about_us_footer = models.TextField(default="توضیحات کوتاه درباره فروشگاه شما...", verbose_name="متن فوتر")
    phone_number = models.CharField(max_length=50, default="12345678 - 021", verbose_name="شماره پشتیبانی")
    working_hours = models.CharField(max_length=255, default="۲۴ ساعته شبانه روز", verbose_name="ساعات پاسخگویی")
    
    seller_legal_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('نام شخص حقیقی / حقوقی'))
    seller_address = models.TextField(null=True, blank=True, verbose_name=_('آدرس کامل فروشگاه'))
    seller_economic_code = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('شماره اقتصادی'))
    seller_postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('کد پستی'))
    seller_registration_number = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('شماره ثبت / شناسه ملی'))
    
    telegram = models.URLField(blank=True, null=True, verbose_name="لینک تلگرام")
    instagram = models.URLField(blank=True, null=True, verbose_name="لینک اینستاگرام")
    whatsapp = models.URLField(blank=True, null=True, verbose_name="لینک واتساپ")
    linkedin = models.URLField(blank=True, null=True, verbose_name="لینک لینکدین")
    twitter = models.URLField(blank=True, null=True, verbose_name="لینک توییتر")
    
    namad_1_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 1")
    namad_1_link = models.URLField(blank=True, null=True, verbose_name="لینک نماد 1")
    
    namad_2_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 2")
    namad_2_link = models.URLField(blank=True, null=True, verbose_name="لینک نماد 2")
    
    namad_3_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 3")
    namad_3_link = models.URLField(blank=True, null=True, verbose_name="لینک نماد 3")
    
    namad_4_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 4")
    namad_4_link = models.URLField(blank=True, null=True, verbose_name="لینک نماد 4")
    
    namad_5_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 5")
    namad_5_link = models.URLField(blank=True, null=True, verbose_name="لینک نماد 5")
    
    namad_6_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 6")
    namad_6_link = models.URLField(blank=True, null=True, verbose_name="لینک نماد 6")
    
    namad_7_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 7")
    namad_7_link = models.URLField(blank=True, null=True, verbose_name="لینک نماد 7")

    copyright_text = models.CharField(max_length=255, default="کلیه حقوق این سایت محفوظ است.", verbose_name="متن کپی‌رایت")

    class Meta:
        verbose_name = _('تنظیمات سایت')
        verbose_name_plural = _('تنظیمات سایت')

    def save(self, *args, **kwargs) -> None:
        """Ensure only one instance exists (Singleton pattern)."""
        if self.__class__.objects.exists() and not self.pk:
            raise ValidationError(_("تنها یک رکورد برای تنظیمات سایت مجاز است."))
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """Prevent deletion of the singleton instance."""
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return self.site_name or _("تنظیمات کلی فروشگاه")


class FAQ(UUIDBaseModel, TimeStampMixin):
    """
    Model for managing Frequently Asked Questions (FAQs).
    """
    question: str = models.CharField(max_length=255, verbose_name=_('پرسش'))
    answer: str = models.TextField(verbose_name=_('پاسخ'))
    order: int = models.PositiveIntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('سوال متداول')
        verbose_name_plural = _('سوالات متداول')
        ordering = ['order', '-created_at']

    def __str__(self) -> str:
        return self.question


class AboutPage(UUIDBaseModel, TimeStampMixin):
    """
    Model for managing dynamic content of the About Us page.
    """
    title: str = models.CharField(max_length=255, verbose_name=_('عنوان صفحه'))
    content: str = models.TextField(verbose_name=_('محتوای متنی اصلی'))
    image = models.ImageField(upload_to='site/about/', null=True, blank=True, verbose_name=_('تصویر شاخص صفحه'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('محتوای درباره ما')
        verbose_name_plural = _('محتوای درباره ما')

    def __str__(self) -> str:
        return self.title