from django.db import models
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin

class Category(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """Product Category Model."""
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name='دسته بندی پدر'
    )
    image = models.ImageField(upload_to='categories/images/', null=True, blank=True, verbose_name='تصویر')
    image_alt = models.CharField(max_length=255, null=True, blank=True, verbose_name='متن جایگزین تصویر (Alt)')
    
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش', help_text='عدد کوچکتر در منوها بالاتر نمایش داده می‌شود.')
    
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name: str = 'دسته بندی'
        verbose_name_plural: str = 'دسته بندی ها'
        ordering = ['order', '-created_at'] 
        indexes: list = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['order']),
        ]

    def __str__(self) -> str:
        return str(self.title)