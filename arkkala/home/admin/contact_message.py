from django.contrib import admin
from home.models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display: tuple = ('full_name', 'phone_number', 'subject', 'is_read', 'created_at')
    list_filter: tuple = ('is_read', 'created_at')
    search_fields: tuple = ('full_name', 'phone_number', 'email', 'subject', 'message')
    list_editable: tuple = ('is_read',)
    readonly_fields: tuple = ('full_name', 'phone_number', 'email', 'subject', 'message', 'created_at')