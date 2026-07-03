"""
Django Admin configuration for shop models.
"""
from django.contrib import admin
from .models import Category, Brand, Attribute, AttributeValue, Product, ProductGallery, ProductVariant, Comment


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ('attribute_values',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display: tuple = ('title', 'brand', 'base_price', 'base_inventory', 'sold_count', 'view_count', 'is_active')
    list_filter: tuple = ('is_active', 'is_variable', 'category', 'brand')
    search_fields: tuple = ('title', 'english_title')
    readonly_fields: tuple = ('sold_count', 'view_count', 'average_rating')
    inlines: list = [ProductGalleryInline, ProductVariantInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display: tuple = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter: tuple = ('is_approved', 'rating')
    actions: list = ['approve_comments']

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_comments(self, request, queryset) -> None:
        queryset.update(is_approved=True)


admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Attribute)
admin.site.register(AttributeValue)