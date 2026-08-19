from typing import Optional, Any
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from platform_tools.mixins.models.base import TimeStampMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, username: str, password: Optional[str] = None, **extra_fields: Any) -> Any:
        if not username:
            raise ValueError(_('شناسه کاربری الزامی است.'))
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: Optional[str] = None, **extra_fields: Any) -> Any:
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, password, **extra_fields)

class User(TimeStampMixin, AbstractUser):
    """
    Unified domain model representing authenticated platform actors.
    """
    email = models.EmailField(_('آدرس ایمیل'), unique=True, null=True, blank=True)
    phone_number = models.CharField(_('شماره تماس'), max_length=15, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True, verbose_name=_('تصویر پروفایل'))
    
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]

    def clean(self) -> None:
        super().clean()
        if self.email == "":
            self.email = None
            
        if self.phone_number == "":
            self.phone_number = None
            
        if not self.email and not self.phone_number:
            raise ValidationError(_('وارد کردن ایمیل یا شماره تماس الزامی است.'))

    def __str__(self) -> str:
        return str(self.phone_number or self.email or self.username)