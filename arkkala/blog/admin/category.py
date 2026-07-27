# arkkala/blog/admin/category.py
from django.contrib import admin
from blog.models.category import Category
from .constants import SEO_FIELDSET

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category."""
    list_display = ('title', 'slug', 'is_active', 'created_at')
    search_fields = ('title', 'slug')
    list_editable = ('is_active',)
    fieldsets = (
        ('اطلاعات پایه', {'fields': ('title', 'slug', 'is_active')}),
        SEO_FIELDSET,
    )