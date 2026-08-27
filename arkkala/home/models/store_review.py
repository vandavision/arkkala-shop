from django.db import models
from django.utils.translation import gettext_lazy as _
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin

class StoreReview(UUIDBaseModel, TimeStampMixin):
    """
    Static reviews about the store for the homepage footer section.
    """
    user_name: str = models.CharField(max_length=150, verbose_name=_('نام کاربر'))
    body: str = models.TextField(verbose_name=_('متن نظر'))
    is_active: bool = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name: str = _('نظر درباره فروشگاه')
        verbose_name_plural: str = _('نظرات درباره فروشگاه')
        ordering: list[str] = ['-created_at']

    def __str__(self) -> str:
        return str(self.user_name)