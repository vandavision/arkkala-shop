from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

class Banner(UUIDBaseModel, TimeStampMixin):
    """
    Promotional Banners placed between sections.
    """
    title: str = models.CharField(max_length=255, verbose_name=_('عنوان بنر'))
    image = models.ImageField(upload_to='home/banners/', verbose_name=_('تصویر بنر'))
    link: str = models.URLField(null=True, blank=True, verbose_name=_('لینک هدایت'))
    position: str = models.CharField(max_length=50, help_text=_('مثال: top_left, middle_row'), verbose_name=_('موقعیت نمایش'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name: str = _('بنر تبلیغاتی')
        verbose_name_plural: str = _('بنرهای تبلیغاتی')

    def __str__(self) -> str:
        return f"{self.title} ({self.position})"