from typing import Tuple, Optional
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from shop.models.category import Category
from .product import SEO_FIELDSET

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'slug', 'parent', 'display_order', 'is_active')
    search_fields = ('title', 'slug')
    list_filter = ('is_active', 'parent')
    
    list_editable = ('is_active',) 
    
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    autocomplete_fields = ('parent',)
    
    fieldsets = (
        ('اطلاعات پایه‌ای', {'fields': ('title', 'slug', 'parent', 'image', 'image_alt', 'order', 'is_active')}),
        SEO_FIELDSET,
        ('اطلاعات سیستمی', {'fields': ('uuid', 'created_at', 'modified_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='ترتیب نمایش', ordering='order')
    def display_order(self, obj: Category) -> str:
        if obj.parent is None:
            return str(obj.order)
        return "-"

    def get_readonly_fields(self, request: HttpRequest, obj: Optional[Category] = None) -> Tuple:
        if obj and obj.parent is not None:
            return self.readonly_fields + ('order',)
        return self.readonly_fields

    def image_preview(self, obj: Category) -> str:
        if obj.image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'تصویر'