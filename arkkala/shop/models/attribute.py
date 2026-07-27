# shop/models/attribute.py
from django.db import models
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin


class Attribute(UUIDBaseModel, TimeStampMixin, TitleSlugMixin):
    """Product Attribute Key."""
    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی ها'

    def __str__(self) -> str:
        return str(self.title)


class AttributeValue(UUIDBaseModel):
    """Product Attribute Value."""
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name='ویژگی')
    value = models.CharField(max_length=255, verbose_name='مقدار')

    class Meta:
        verbose_name = 'مقدار ویژگی'
        verbose_name_plural = 'مقادیر ویژگی'

    def __str__(self) -> str:
        return f"{self.attribute.title}: {self.value}"