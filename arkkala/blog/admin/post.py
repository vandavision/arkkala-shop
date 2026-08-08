from django.contrib import admin
from blog.models.post import Post
from blog.models.comment import Comment
from .constants import SEO_FIELDSET

class CommentInline(admin.TabularInline):
    """
    Configures embedded object modification securely preventing layout errors completely.
    """
    model = Comment
    extra: int = 0
    readonly_fields: tuple = ('user', 'body', 'created_at')
    classes: tuple = ('collapse',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Provides broad metadata definitions managing heavy associations gracefully.
    """
    list_display: tuple = ('title', 'category', 'author', 'view_count', 'is_published', 'created_at')
    list_filter: tuple = ('is_published', 'category', 'tags', 'created_at')
    search_fields: tuple = ('title', 'short_description', 'slug')
    readonly_fields: tuple = ('uuid', 'view_count', 'created_at', 'modified_at')
    filter_horizontal: tuple = ('tags',)
    autocomplete_fields: tuple = ('category', 'author')
    inlines: list = [CommentInline]
    save_on_top: bool = True
    
    fieldsets: tuple = (
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
        ('اطلاعات سیستمی', {
            'fields': ('uuid', 'created_at', 'modified_at'),
            'classes': ('collapse',)
        }),
    )