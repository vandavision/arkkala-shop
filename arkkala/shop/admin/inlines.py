# shop/admin/inlines.py
from typing import Any, Optional
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from shop.models.attribute import AttributeValue
from shop.models.product import ProductGallery, ProductVideo, ProductVariant, PriceHistory


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    classes = ['collapse']


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    readonly_fields = ('image_preview',)
    fields = ('image', 'image_alt', 'image_preview', 'is_main')
    classes = ['collapse']

    def image_preview(self, obj: ProductGallery) -> str:
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius: 5px; object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'پیش‌نمایش'


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    classes = ['collapse']


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    autocomplete_fields = ('attribute_values',)
    fields = ('attribute_values', 'price', 'wholesale_price', 'inventory', 'gallery_image')
    classes = ['collapse']

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "gallery_image":
            if getattr(request, 'resolver_match', None) and request.resolver_match.kwargs.get('object_id'):
                kwargs["queryset"] = ProductGallery.objects.filter(product_id=request.resolver_match.kwargs.get('object_id'))
            else:
                kwargs["queryset"] = ProductGallery.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('price', 'created_at')
    can_delete = False
    classes = ['collapse']

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False