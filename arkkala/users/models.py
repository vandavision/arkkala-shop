"""
Custom User Model and OTP/Reset Security Models.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import uuid
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin
from django.conf import settings

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
    """Model to track OTP requests (both SMS and Email Reset) and prevent Bombing."""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    identifier = models.CharField(max_length=255, verbose_name=_('شناسه (تلفن/ایمیل)'))
    code = models.CharField(max_length=6, verbose_name=_('کد تایید'))
    ip_address = models.GenericIPAddressField(verbose_name=_('آدرس IP'))
    is_used = models.BooleanField(default=False, verbose_name=_('استفاده شده؟'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _('درخواست کد یکبار مصرف')
        verbose_name_plural = _('درخواست‌های کدهای یکبار مصرف')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            from django.conf import settings
            wait_time = getattr(settings, 'OTP_WAIT_TIME_MINUTES', 2)
            self.expires_at = timezone.now() + timedelta(minutes=wait_time)
        super().save(*args, **kwargs)

class UserAddress(UUIDBaseModel, TimeStampMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses', verbose_name=_('کاربر'))
    title = models.CharField(max_length=100, verbose_name=_('عنوان آدرس'), help_text=_('مثال: خانه، محل کار'))
    recipient_first_name = models.CharField(max_length=150, verbose_name=_('نام تحویل گیرنده'))
    recipient_last_name = models.CharField(max_length=150, verbose_name=_('نام خانوادگی تحویل گیرنده'))
    recipient_phone = models.CharField(max_length=20, verbose_name=_('شماره تماس تحویل گیرنده'))
    province = models.CharField(max_length=100, verbose_name=_('استان'))
    city = models.CharField(max_length=100, verbose_name=_('شهر'))
    postal_address = models.TextField(verbose_name=_('آدرس پستی'))
    postal_code = models.CharField(max_length=20, verbose_name=_('کد پستی'))
    plaque = models.CharField(max_length=20, verbose_name=_('پلاک'))
    building_unit = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('واحد'))
    is_default = models.BooleanField(default=False, verbose_name=_('آدرس پیش‌فرض'))

    class Meta:
        verbose_name = _('آدرس کاربر')
        verbose_name_plural = _('آدرس‌های کاربران')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.user}"

    def save(self, *args, **kwargs):
        if self.is_default:
            UserAddress.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)