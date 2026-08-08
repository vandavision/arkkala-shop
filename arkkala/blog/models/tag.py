from django.db import models
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin

class Tag(UUIDBaseModel, TimeStampMixin, TitleSlugMixin):
    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب ها'
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self) -> str:
        return str(self.title)