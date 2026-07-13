"""
Django Admin configuration for shop models.
Exposes all SEO, AEO, and GEO functionality flawlessly.
"""
from typing import Any, List, Optional, Tuple

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Attribute, AttributeValue, Brand, Category, Comment, PriceHistory,
    Product, ProductGallery, ProductVariant, ProductVideo, Question,
)


SEO_FIELDSET: Tuple[str, dict] = (
    _('تنظیمات سئو (SEO) و OpenGraph'),
    {
        'fields': (
            'keywords', 'meta_description', 'og_title', 'og_type', 'og_image',
            'og_description', 'og_url', 'og_site_name', 'og_locale', 'article_author',
            'twitter_card', 'twitter_site', 'twitter_creator'
        ),
        'classes': ('collapse',),
    },
)

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
    image_preview.short_description = _('پیش‌نمایش')


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    classes = ['collapse']


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    autocomplete_fields = ('attribute_values',)
    fields = ('attribute_values', 'price', 'wholesale_price', 'inventory')
    classes = ['collapse']


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('price', 'created_at')
    can_delete = False
    classes = ['collapse']

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'slug', 'parent', 'is_active')
    search_fields = ('title', 'slug')
    list_editable = ('is_active',)
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    autocomplete_fields = ('parent',)
    
    fieldsets = (
        (_('اطلاعات پایه‌ای'), {
            'fields': ('title', 'slug', 'parent', 'image', 'image_alt', 'is_active')
        }),
        SEO_FIELDSET,
        (_('اطلاعات سیستمی'), {
            'fields': ('uuid', 'created_at', 'modified_at'),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj: Category) -> str:
        if obj.image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = _('تصویر')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'title', 'slug', 'is_active')
    search_fields = ('title', 'slug')
    list_editable = ('is_active',)
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    
    fieldsets = (
        (_('اطلاعات پایه‌ای'), {
            'fields': ('title', 'slug', 'logo', 'logo_alt', 'is_active')
        }),
        SEO_FIELDSET,
        (_('اطلاعات سیستمی'), {
            'fields': ('uuid', 'created_at', 'modified_at'),
            'classes': ('collapse',),
        }),
    )

    def logo_preview(self, obj: Brand) -> str:
        if obj.logo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = _('لوگو')


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'brand', 'base_price', 'base_inventory',
        'is_variable', 'is_active', 'special_offer_status'
    )
    list_filter = ('is_active', 'is_variable', 'category', 'brand')
    search_fields = ('title', 'english_title', 'slug')
    list_editable = ('is_active', 'is_variable', 'base_price', 'base_inventory')
    autocomplete_fields = ('category', 'brand', 'favorites')
    readonly_fields = ('uuid', 'sold_count', 'view_count', 'average_rating', 'created_at', 'modified_at')
    inlines = [ProductGalleryInline, ProductVideoInline, ProductVariantInline, PriceHistoryInline]
    filter_horizontal = ('favorites',)
    save_on_top = True

    fieldsets = (
        (_('اطلاعات اصلی'), {
            'fields': ('title', 'english_title', 'slug', 'category', 'brand', 'short_description', 'description')
        }),
        (_('هوش مصنوعی مولد و اعتبار (GEO)'), {
            'fields': ('expert_reviewer', 'key_takeaways', 'citations'),
            'description': 'فیلدهای الزامی برای تسخیر پاسخ‌های ChatGPT، Gemini و SGE.'
        }),
        (_('مشخصات فیزیکی'), {
            'fields': ('weight', 'volume'),
            'classes': ('collapse',),
        }),
        (_('قیمت و موجودی پایه‌ای'), {
            'fields': ('base_price', 'base_inventory', 'is_variable', 'is_active')
        }),
        (_('تخفیف و فروش عمده'), {
            'fields': (
                'special_discount_percent', 'special_offer_end',
                'is_wholesale', 'wholesale_min_quantity', 'wholesale_base_price'
            ),
            'classes': ('collapse',),
        }),
        SEO_FIELDSET,
        (_('داده‌های ساختاریافته (JSON-LD)'), {
            'fields': ('json_ld',),
            'classes': ('collapse',),
        }),
        (_('آمار سیستم'), {
            'fields': ('favorites', 'sold_count', 'view_count', 'average_rating'),
            'classes': ('collapse',),
        }),
        (_('اطلاعات سیستمی'), {
            'fields': ('uuid', 'created_at', 'modified_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description=_('وضعیت تخفیف'), boolean=True)
    def special_offer_status(self, obj: Product) -> bool:
        return obj.is_special_offer_active


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('body', 'product__title')
    autocomplete_fields = ('product', 'user')
    list_editable = ('is_approved',)
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    actions = ['approve_comments', 'reject_comments']

    fieldsets = (
        (None, {
            'fields': ('product', 'user', 'body', 'rating', 'is_approved')
        }),
        (_('اطلاعات سیستمی'), {
            'fields': ('uuid', 'created_at', 'modified_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.action(description=_('تایید نظرات انتخاب شده'))
    def approve_comments(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated: int = queryset.update(is_approved=True)
        self.message_user(request, _(f"{updated} نظر با موفقیت تایید شد."))

    @admin.action(description=_('رد نظرات انتخاب شده'))
    def reject_comments(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated: int = queryset.update(is_approved=False)
        self.message_user(request, _(f"{updated} نظر رد شد."))


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_author_name', 'is_approved', 'has_answer', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('text', 'answer_text', 'product__title', 'name')
    autocomplete_fields = ('product', 'user')
    list_editable = ('is_approved',)
    readonly_fields = ('uuid', 'created_at', 'modified_at')
    actions = ['approve_questions']

    fieldsets = (
        (_('اطلاعات پرسش'), {'fields': ('product', 'user', 'name', 'text', 'is_approved')}),
        (_('پاسخ (مولد AEO)'), {
            'fields': ('answer_text',),
            'description': 'ارائه پاسخ دقیق در این فیلد، مستقیماً به اسکیمای FAQ محصول اضافه شده و باعث رشد شدید سئوی صوتی و AEO می‌شود.'
        }),
        (_('اطلاعات سیستمی'), {
            'fields': ('uuid', 'created_at', 'modified_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description=_('پرسشگر'))
    def get_author_name(self, obj: Question) -> str:
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return obj.name or _('مهمان')

    @admin.display(description=_('پاسخ داده شده؟'), boolean=True)
    def has_answer(self, obj: Question) -> bool:
        return bool(obj.answer_text and obj.answer_text.strip())

    @admin.action(description=_('تایید پرسش‌ها'))
    def approve_questions(self, request: HttpRequest, queryset: QuerySet) -> None:
        updated: int = queryset.update(is_approved=True)
        self.message_user(request, _(f"{updated} پرسش با موفقیت تایید شد."))


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'created_at')
    search_fields = ('product__title',)
    autocomplete_fields = ('product',)
    readonly_fields = ('uuid', 'product', 'price', 'created_at')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
        
    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False