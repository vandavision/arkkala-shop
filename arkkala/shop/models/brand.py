from django.db import models
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin

class Brand(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """
    Product Brand Model.
    """
    logo = models.ImageField(upload_to='brands/logos/', null=True, blank=True, verbose_name='لوگو')
    logo_alt = models.CharField(max_length=255, null=True, blank=True, verbose_name='متن جایگزین لوگو (Alt)')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name: str = 'برند'
        verbose_name_plural: str = 'برند ها'
        indexes: list = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return str(self.title)