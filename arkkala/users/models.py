"""
Custom User Model and OTP Security Models.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import uuid


class CustomUserManager(BaseUserManager):
    """Unified Manager to handle both Email and Phone creations."""
    
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_('شناسه کاربری (ایمیل یا شماره تلفن) الزامی است.'))
        
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    """
    Unified User Model. 
    `username` is used internally to store either the phone number or the email seamlessly.
    """
    email = models.EmailField(_('آدرس ایمیل'), unique=True, null=True, blank=True)
    phone_number = models.CharField(_('شماره تماس'), max_length=15, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True, verbose_name=_('تصویر پروفایل'))
    
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        ordering = ['-date_joined']

    def __str__(self) -> str:
        return self.phone_number or self.email or self.username


class OTPRequest(models.Model):
    """Model to track OTP requests and prevent SMS Bombing."""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(max_length=15, verbose_name=_('شماره تماس'))
    code = models.CharField(max_length=6, verbose_name=_('کد تایید'))
    ip_address = models.GenericIPAddressField(verbose_name=_('آدرس IP'))
    is_used = models.BooleanField(default=False, verbose_name=_('استفاده شده؟'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _('درخواست پیامک')
        verbose_name_plural = _('درخواست‌های پیامک')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            from django.conf import settings
            wait_time = getattr(settings, 'OTP_WAIT_TIME_MINUTES', 2)
            self.expires_at = timezone.now() + timedelta(minutes=wait_time)
        super().save(*args, **kwargs)