from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

class Story(UUIDBaseModel, TimeStampMixin):
    """
    Instagram-like Stories for the home page supporting images and videos.
    """
    title: str = models.CharField(max_length=100, verbose_name=_('عنوان استوری'))
    image = models.ImageField(upload_to='home/stories/', verbose_name=_('تصویر کاور استوری'))
    video = models.FileField(upload_to='home/stories/videos/', null=True, blank=True, verbose_name=_('ویدیوی استوری'))
    link: str = models.URLField(null=True, blank=True, verbose_name=_('لینک هدایت'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال/نمایش'))

    class Meta:
        verbose_name: str = _('استوری')
        verbose_name_plural: str = _('استوری‌ها')
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return str(self.title)