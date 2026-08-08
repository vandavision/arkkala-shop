from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin

class Category(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """
    Category entity for blog post taxonomy organization.
    """
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name: str = _('دسته بندی مقالات')
        verbose_name_plural: str = _('دسته بندی های مقالات')
        indexes: list = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        """
        Returns the string representation of the Category.
        """
        return str(self.title)