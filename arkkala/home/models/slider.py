from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

class Slider(UUIDBaseModel, TimeStampMixin):
    """
    Main Carousel Sliders.
    """
    title: str = models.CharField(max_length=255, verbose_name=_('عنوان اسلایدر'))
    image = models.ImageField(upload_to='home/sliders/', verbose_name=_('تصویر اسلایدر'))
    link: str = models.URLField(null=True, blank=True, verbose_name=_('لینک هدایت'))
    order: int = models.PositiveIntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name: str = _('اسلایدر')
        verbose_name_plural: str = _('اسلایدرها')
        ordering: list[str] = ['order', '-created_at']

    def __str__(self) -> str:
        return str(self.title)