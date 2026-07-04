"""
Django Admin configuration for blog models.
"""
from django.contrib import admin
from django.http import HttpRequest
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Categories."""
    list_display = ('title', 'slug', 'is_active', 'created_at')
    search_fields = ('title',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Tags."""
    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title',)


class CommentInline(admin.TabularInline):
    """Inline Admin for Blog Comments."""
    model = Comment
    extra = 0
    readonly_fields = ('user', 'body', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Posts."""
    list_display = ('title', 'category', 'author', 'view_count', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'tags')
    search_fields = ('title', 'short_description')
    readonly_fields = ('view_count',)
    filter_horizontal = ('tags',)
    inlines = [CommentInline]
    
    fieldsets = (
        ('اطلاعات مقاله', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'image')
        }),
        ('محتوا', {
            'fields': ('short_description', 'body', 'read_time')
        }),
        ('وضعیت و آمار', {
            'fields': ('is_published', 'view_count')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Comments."""
    list_display = ('post', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('body', 'user__username')
    actions = ['approve_comments']

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request: HttpRequest, queryset) -> None:
        """Approve selected comments."""
        queryset.update(is_approved=True)