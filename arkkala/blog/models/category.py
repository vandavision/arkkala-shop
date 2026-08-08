from django.db import models
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin

class Category(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'دسته بندی مقالات'
        verbose_name_plural = 'دسته بندی های مقالات'
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return str(self.title)