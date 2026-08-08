from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin

class Tag(UUIDBaseModel, TimeStampMixin, TitleSlugMixin):
    """
    Tag entity for precise content categorization and indexing.
    """
    class Meta:
        verbose_name: str = _('برچسب')
        verbose_name_plural: str = _('برچسب ها')
        indexes: list = [
            models.Index(fields=['slug']),
        ]

    def __str__(self) -> str:
        """
        Returns the string representation of the Tag.
        """
        return str(self.title)