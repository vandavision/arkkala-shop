from django.contrib import admin
from blog.models.tag import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Administration component displaying simplified schema strictly.
    """
    list_display: tuple = ('title', 'slug', 'created_at')
    search_fields: tuple = ('title', 'slug')
    readonly_fields: tuple = ('uuid', 'created_at', 'modified_at')