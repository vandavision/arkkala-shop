# arkkala/blog/admin/post.py
from django.contrib import admin
from blog.models.post import Post
from blog.models.comment import Comment
from .constants import SEO_FIELDSET

class CommentInline(admin.TabularInline):
    """Inline admin for Comment."""
    model = Comment
    extra = 0
    readonly_fields = ('user', 'body', 'created_at')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post."""
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
        }),
        ('موتورهای پاسخگو (AEO)', {
            'fields': ('faq_data',),
        }),
        SEO_FIELDSET,
        ('وضعیت و آمار', {
            'fields': ('is_published', 'view_count', 'json_ld')
        }),
    )