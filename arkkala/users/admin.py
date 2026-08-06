from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from users.models.user import User
from users.models.otp import OTPRequest
from users.models.address import UserAddress

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom interface configured accurately for unified user access mapping correctly.
    """
    list_display = ('email', 'phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        (_('اطلاعات شخصی'), {'fields': ('first_name', 'last_name', 'avatar')}),
        (_('دسترسی ها'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('تاریخ های مهم'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password', 'first_name', 'last_name', 'is_active', 'is_staff'),
        }),
    )

@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    """
    Exposes strict control over monitoring requests.
    """
    list_display = ('identifier', 'code', 'is_used', 'ip_address', 'created_at', 'expires_at')
    search_fields = ('identifier', 'ip_address')
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('uuid', 'created_at')

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """
    Monitors address inputs logically and safely.
    """
    list_display = ('title', 'user', 'recipient_phone', 'city', 'is_default')
    search_fields = ('title', 'user__email', 'user__phone_number', 'recipient_phone')
    list_filter = ('is_default', 'province', 'city')
    readonly_fields = ('uuid', 'created_at', 'modified_at')