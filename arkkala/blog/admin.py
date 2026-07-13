"""
Django Admin configuration for blog models.
Optimized to expose SEO, AEO, and GEO fields cleanly without removing any existing logic.
"""
from django.contrib import admin
from django.http import HttpRequest
from typing import Any, Tuple

from .models import Category, Tag, Post, Comment


SEO_FIELDSET: Tuple[str, dict] = (
    'تنظیمات سئو (SEO) و OpenGraph',
    {
        'fields': (
            'keywords',
            'meta_description',
            'og_title',
            'og_type',
            'og_image',
            'og_description',
            'og_url',
            'og_site_name',
            'og_locale',
            'article_author',
            'twitter_card',
            'twitter_creator',
            'twitter_site'
        ),
        'classes': ('collapse',),
    },
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Categories."""
    list_display = ('title', 'slug', 'is_active', 'created_at')
    search_fields = ('title', 'slug')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('اطلاعات پایه', {'fields': ('title', 'slug', 'is_active')}),
        SEO_FIELDSET,
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Tags."""
    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title', 'slug')


class CommentInline(admin.TabularInline):
    """Inline Admin for Blog Comments."""
    model = Comment
    extra = 0
    readonly_fields = ('user', 'body', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Posts."""
    list_display = ('title', 'category', 'author', 'view_count', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'tags', 'created_at')
    search_fields = ('title', 'short_description', 'slug')
    readonly_fields = ('view_count',)
    filter_horizontal = ('tags',)
    inlines = [CommentInline]
    save_on_top = True
    
    fieldsets = (
        ('اطلاعات مقاله', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'image', 'image_alt')
        }),
        ('محتوا', {
            'fields': ('short_description', 'body', 'read_time')
        }),
        ('هوش مصنوعی مولد و اعتبار (GEO)', {
            'fields': ('expert_reviewer', 'key_takeaways', 'citations'),
            'description': 'فیلدهای E-E-A-T و ساختاریافته برای گرفتن بالاترین امتیاز در هوش‌های مصنوعی مثل ChatGPT و SGE.'
        }),
        ('موتورهای پاسخگو (AEO)', {
            'fields': ('faq_data',),
            'description': 'سوالات متداول که مستقیماً به اسکیمای FAQ تبدیل شده و در جستجوی صوتی نمایش داده می‌شوند.'
        }),
        SEO_FIELDSET,
        ('وضعیت و آمار', {
            'fields': ('is_published', 'view_count', 'json_ld')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin Interface for Blog Comments."""
    list_display = ('post', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('body', 'user__first_name', 'user__last_name', 'user__phone_number')
    actions = ['approve_comments']
    list_editable = ('is_approved',)

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request: HttpRequest, queryset: Any) -> None:
        """Approve selected comments."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} نظر با موفقیت تایید شد.")