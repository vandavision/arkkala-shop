# arkkala/blog/models/tag.py
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin

class Tag(UUIDBaseModel, TimeStampMixin, TitleSlugMixin):
    """Tag model for blog posts."""
    class Meta:
        verbose_name = _('برچسب')
        verbose_name_plural = _('برچسب ها')

    def __str__(self) -> str:
        return str(self.title)