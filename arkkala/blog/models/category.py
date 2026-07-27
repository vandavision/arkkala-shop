# arkkala/blog/models/category.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin

class Category(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """Category model for organizing blog posts."""
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('دسته بندی مقالات')
        verbose_name_plural = _('دسته بندی های مقالات')

    def __str__(self) -> str:
        return str(self.title)