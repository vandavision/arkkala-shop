from django.contrib import admin
from users.models.address import UserAddress

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """
    Monitors logistics entries mapped to actors safely.
    """
    list_display = ('title', 'user', 'recipient_phone', 'city', 'is_default')
    search_fields = ('title', 'user__email', 'user__phone_number', 'recipient_phone')
    list_filter = ('is_default', 'province', 'city')
    readonly_fields = ('uuid', 'created_at', 'modified_at')