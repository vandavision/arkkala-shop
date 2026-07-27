# shop/admin/brand.py
from django.contrib import admin
from django.utils.html import format_html
from shop.models.brand import Brand
from .product import SEO_FIELDSET


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'title', 'slug', 'is_active')
    search_fields = ('title', 'slug')
    list_editable = ('is_active',)
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    
    fieldsets = (
        ('اطلاعات پایه‌ای', {'fields': ('title', 'slug', 'logo', 'logo_alt', 'is_active')}),
        SEO_FIELDSET,
        ('اطلاعات سیستمی', {'fields': ('uuid', 'created_at', 'modified_at'), 'classes': ('collapse',)}),
    )

    def logo_preview(self, obj: Brand) -> str:
        if obj.logo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'لوگو'