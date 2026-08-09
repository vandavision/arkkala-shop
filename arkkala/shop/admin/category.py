from django.contrib import admin
from django.utils.html import format_html
from shop.models.category import Category
from .product import SEO_FIELDSET

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'slug', 'parent', 'is_active')
    search_fields = ('title', 'slug')
    list_editable = ('is_active',)
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    autocomplete_fields = ('parent',)
    
    fieldsets = (
        ('اطلاعات پایه‌ای', {'fields': ('title', 'slug', 'parent', 'image', 'image_alt', 'is_active')}),
        SEO_FIELDSET,
        ('اطلاعات سیستمی', {'fields': ('uuid', 'created_at', 'modified_at'), 'classes': ('collapse',)}),
    )

    def image_preview(self, obj: Category) -> str:
        if obj.image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'تصویر'