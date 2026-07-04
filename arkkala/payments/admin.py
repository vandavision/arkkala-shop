from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'amount', 'gateway', 'status', 'ref_id', 'created_at')
    list_filter = ('status', 'gateway', 'created_at')
    search_fields = ('user__username', 'user__email', 'authority', 'ref_id', 'order__uuid')
    readonly_fields = ('user', 'order', 'amount', 'gateway', 'authority', 'ref_id', 'status', 'description')
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False