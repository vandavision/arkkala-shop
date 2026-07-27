# arkkala/blog/admin/tag.py
from django.contrib import admin
from blog.models.tag import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag."""
    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title', 'slug')