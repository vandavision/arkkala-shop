from typing import Self
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from home.domain.exceptions import SingletonConstraintException

class SiteSetting(models.Model):
    """
    Singleton model for global site settings.
    """
    site_name: str = models.CharField(max_length=255, default="ارک کالا", verbose_name="نام سایت")
    logo = models.ImageField(upload_to="site/logo/", null=True, blank=True, verbose_name="لوگوی اصلی")
    about_us_footer: str = models.TextField(default="توضیحات کوتاه درباره فروشگاه شما...", verbose_name="متن فوتر")
    phone_number: str = models.CharField(max_length=50, default="12345678 - 021", verbose_name="شماره پشتیبانی")
    working_hours: str = models.CharField(max_length=255, default="۲۴ ساعته شبانه روز", verbose_name="ساعات پاسخگویی")
    
    seller_legal_name: str = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('نام شخص حقیقی / حقوقی'))
    seller_address: str = models.TextField(null=True, blank=True, verbose_name=_('آدرس کامل فروشگاه'))
    seller_economic_code: str = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('شماره اقتصادی'))
    seller_postal_code: str = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('کد پستی'))
    seller_registration_number: str = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('شماره ثبت / شناسه ملی'))
    
    telegram: str = models.URLField(blank=True, null=True, verbose_name="لینک تلگرام")
    instagram: str = models.URLField(blank=True, null=True, verbose_name="لینک اینستاگرام")
    whatsapp: str = models.URLField(blank=True, null=True, verbose_name="لینک واتساپ")
    linkedin: str = models.URLField(blank=True, null=True, verbose_name="لینک لینکدین")
    twitter: str = models.URLField(blank=True, null=True, verbose_name="لینک توییتر")
    
    namad_1_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 1")
    namad_1_link: str = models.URLField(blank=True, null=True, verbose_name="لینک نماد 1")
    namad_2_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 2")
    namad_2_link: str = models.URLField(blank=True, null=True, verbose_name="لینک نماد 2")
    namad_3_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 3")
    namad_3_link: str = models.URLField(blank=True, null=True, verbose_name="لینک نماد 3")
    namad_4_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 4")
    namad_4_link: str = models.URLField(blank=True, null=True, verbose_name="لینک نماد 4")
    namad_5_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 5")
    namad_5_link: str = models.URLField(blank=True, null=True, verbose_name="لینک نماد 5")
    namad_6_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 6")
    namad_6_link: str = models.URLField(blank=True, null=True, verbose_name="لینک نماد 6")
    namad_7_img = models.ImageField(upload_to="site/namad/", blank=True, null=True, verbose_name="عکس نماد 7")
    namad_7_link: str = models.URLField(blank=True, null=True, verbose_name="لینک نماد 7")

    copyright_text: str = models.CharField(max_length=255, default="کلیه حقوق این سایت محفوظ است.", verbose_name="متن کپی‌رایت")

    class Meta:
        verbose_name: str = _('تنظیمات سایت')
        verbose_name_plural: str = _('تنظیمات سایت')

    def save(self, *args: tuple, **kwargs: dict) -> None:
        if self.__class__.objects.exists() and not self.pk:
            raise SingletonConstraintException(_("تنها یک رکورد برای تنظیمات سایت مجاز است."))
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args: tuple, **kwargs: dict) -> None:
        pass

    @classmethod
    def load(cls) -> Self:
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return self.site_name or str(_("تنظیمات کلی فروشگاه"))