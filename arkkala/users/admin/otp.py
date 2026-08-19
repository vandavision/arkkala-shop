from django.contrib import admin
from users.models.otp import OTPRequest

@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    """
    Exposes strict control over monitoring access requests natively.
    """
    list_display = ('identifier', 'code', 'is_used', 'ip_address', 'created_at', 'expires_at')
    search_fields = ('identifier', 'ip_address')
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('uuid', 'created_at')