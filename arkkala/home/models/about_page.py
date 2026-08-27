from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

class AboutPage(UUIDBaseModel, TimeStampMixin):
    """
    Model for managing dynamic content of the About Us page.
    """
    title: str = models.CharField(max_length=255, verbose_name=_('عنوان صفحه'))
    content: str = models.TextField(verbose_name=_('محتوای متنی اصلی'))
    image = models.ImageField(upload_to='site/about/', null=True, blank=True, verbose_name=_('تصویر شاخص صفحه'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name: str = _('محتوای درباره ما')
        verbose_name_plural: str = _('محتوای درباره ما')

    def __str__(self) -> str:
        return str(self.title)