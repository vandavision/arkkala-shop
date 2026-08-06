from typing import Optional, Any
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    """
    Manager for handling Custom User creation natively and via OTP/Email workflows.
    """
    def create_user(self, username: str, password: Optional[str] = None, **extra_fields: Any) -> Any:
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError(_('شناسه کاربری (ایمیل یا شماره تلفن) الزامی است.'))
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, password: Optional[str] = None, **extra_fields: Any) -> Any:
        """
        Creates and saves a SuperUser.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractUser):
    """
    Enterprise Unified User Entity.
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
        """
        Validates business constraints strictly at the model level and fixes empty string issues for unique fields.
        """
        super().clean()
        if self.email == "":
            self.email = None
            
        if self.phone_number == "":
            self.phone_number = None
            
        if not self.email and not self.phone_number:
            raise ValidationError(_('وارد کردن ایمیل یا شماره تماس الزامی است.'))

    def __str__(self) -> str:
        """
        String representation prioritizes phone, then email, then username.
        """
        return str(self.phone_number or self.email or self.username)