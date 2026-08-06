from typing import Tuple, Any, Optional
from django.contrib import admin
from django.http import HttpRequest
from shop.models.product import Product, PriceHistory
from .inlines import ProductGalleryInline, ProductVideoInline, ProductVariantInline, PriceHistoryInline

SEO_FIELDSET: Tuple[str, dict] = (
    'تنظیمات سئو (SEO) و OpenGraph',
    {
        'fields': (
            'keywords', 'meta_description', 'og_title', 'og_type', 'og_image',
            'og_description', 'og_url', 'og_site_name', 'og_locale', 'article_author',
            'twitter_card', 'twitter_site', 'twitter_creator'
        ),
        'classes': ('collapse',),
    },
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display: tuple = ('title', 'category', 'brand', 'base_price', 'base_inventory', 'is_variable', 'is_active', 'special_offer_status')
    list_filter: tuple = ('is_active', 'is_variable', 'category', 'brand')
    search_fields: tuple = ('title', 'english_title', 'slug')
    list_editable: tuple = ('is_active', 'is_variable', 'base_price', 'base_inventory')
    autocomplete_fields: tuple = ('category', 'brand', 'favorites')
    readonly_fields: tuple = ('uuid', 'sold_count', 'view_count', 'average_rating', 'created_at', 'modified_at')
    inlines: list = [ProductGalleryInline, ProductVideoInline, ProductVariantInline, PriceHistoryInline]
    filter_horizontal: tuple = ('favorites',)
    save_on_top: bool = True

    fieldsets: tuple = (
        ('اطلاعات اصلی', {'fields': ('title', 'english_title', 'slug', 'category', 'brand', 'short_description', 'description')}),
        ('هوش مصنوعی مولد و اعتبار (GEO)', {'fields': ('expert_reviewer', 'key_takeaways', 'citations')}),
        ('مشخصات فیزیکی', {'fields': ('weight', 'volume'), 'classes': ('collapse',)}),
        ('قیمت و موجودی پایه‌ای', {'fields': ('base_price', 'base_inventory', 'is_variable', 'is_active')}),
        ('تخفیف و فروش عمده', {'fields': ('special_discount_percent', 'special_offer_end', 'is_wholesale', 'wholesale_min_quantity', 'wholesale_base_price'), 'classes': ('collapse',)}),
        SEO_FIELDSET,
        ('داده‌های ساختاریافته (JSON-LD)', {'fields': ('json_ld',), 'classes': ('collapse',)}),
        ('آمار سیستم', {'fields': ('favorites', 'sold_count', 'view_count', 'average_rating'), 'classes': ('collapse',)}),
        ('اطلاعات سیستمی', {'fields': ('uuid', 'created_at', 'modified_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='وضعیت تخفیف', boolean=True)
    def special_offer_status(self, obj: Product) -> bool:
        return obj.is_special_offer_active

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display: tuple = ('product', 'price', 'created_at')
    search_fields: tuple = ('product__title',)
    autocomplete_fields: tuple = ('product',)
    readonly_fields: tuple = ('uuid', 'product', 'price', 'created_at')

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
        
    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False