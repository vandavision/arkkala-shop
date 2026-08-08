from django.contrib import admin
from blog.models.category import Category
from .constants import SEO_FIELDSET

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Administration projection isolating basic hierarchy controls reliably.
    """
    list_display: tuple = ('title', 'slug', 'is_active', 'created_at')
    search_fields: tuple = ('title', 'slug')
    list_editable: tuple = ('is_active',)
    readonly_fields: tuple = ('uuid', 'created_at', 'modified_at')
    
    fieldsets: tuple = (
        ('اطلاعات پایه', {'fields': ('title', 'slug', 'is_active')}),
        SEO_FIELDSET,
        ('اطلاعات سیستمی', {'fields': ('uuid', 'created_at', 'modified_at'), 'classes': ('collapse',)}),
    )