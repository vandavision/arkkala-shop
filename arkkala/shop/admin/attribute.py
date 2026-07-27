# shop/admin/attribute.py
from django.contrib import admin
from shop.models.attribute import Attribute, AttributeValue
from .inlines import AttributeValueInline


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title', 'slug')
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    inlines = [AttributeValueInline]


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'attribute')
    list_filter = ('attribute',)
    search_fields = ('value', 'attribute__title')
    autocomplete_fields = ('attribute',)