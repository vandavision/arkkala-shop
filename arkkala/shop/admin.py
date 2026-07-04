"""
Django Admin configuration for shop models.
"""
from django.contrib import admin
from django.http import HttpRequest
from .models import Category, Brand, Attribute, AttributeValue, Product, ProductGallery, ProductVideo, ProductVariant, Comment


class ProductGalleryInline(admin.TabularInline):
    """Inline Admin for Product Images."""
    model = ProductGallery
    extra = 1


class ProductVideoInline(admin.TabularInline):
    """Inline Admin for Product Videos."""
    model = ProductVideo
    extra = 1


class ProductVariantInline(admin.StackedInline):
    """Inline Admin for Product Variants."""
    model = ProductVariant
    extra = 1
    filter_horizontal = ('attribute_values',)
    fields = ('attribute_values', 'price', 'wholesale_price', 'inventory')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin Interface for Products."""
    list_display: tuple = ('title', 'brand', 'base_price', 'is_wholesale', 'base_inventory', 'sold_count', 'is_active')
    list_filter: tuple = ('is_active', 'is_wholesale', 'is_variable', 'category', 'brand')
    search_fields: tuple = ('title', 'english_title')
    readonly_fields: tuple = ('sold_count', 'view_count', 'average_rating')
    inlines: list = [ProductGalleryInline, ProductVideoInline, ProductVariantInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'english_title', 'slug', 'category', 'brand', 'short_description', 'description')
        }),
        ('فروش تکی و متغیر بودن', {
            'fields': ('is_active', 'is_variable', 'base_price', 'base_inventory')
        }),
        ('فروش عمده', {
            'fields': ('is_wholesale', 'wholesale_min_quantity', 'wholesale_base_price'),
            'description': 'اگر محصول قابلیت فروش عمده دارد، تیک را بزنید و حداقل تعداد و قیمت عمده را وارد کنید.'
        }),
        ('آمار (غیرقابل ویرایش)', {
            'fields': ('sold_count', 'view_count', 'average_rating')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin Interface for Product Comments."""
    list_display: tuple = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter: tuple = ('is_approved', 'rating')
    actions: list = ['approve_comments']

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request: HttpRequest, queryset) -> None:
        """Approve selected comments."""
        queryset.update(is_approved=True)


admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Attribute)
admin.site.register(AttributeValue)