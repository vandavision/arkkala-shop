from decimal import Decimal
from typing import Any, Dict, List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from platform_seo.models.mixins.seo import ProductDetailJsonLdMixin, SEOMixin
from platform_tools.mixins.models.base import (
    TimeStampMixin,
    TitleSlugMixin,
    UUIDBaseModel,
)
from shop.models.attribute import AttributeValue
from shop.models.brand import Brand
from shop.models.category import Category
from shop.models.managers import ProductManager

try:
    from django_jsonform.models.fields import JSONField
except ImportError:
    JSONField = models.JSONField

User = get_user_model()
STRING_LIST_SCHEMA: Dict[str, Any] = {'type': 'array', 'items': {'type': 'string'}}


class Product(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin, ProductDetailJsonLdMixin):
    """Enterprise Product Entity with Strict Validation Rules and Full SEO/AEO/GEO Support."""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='دسته بندی')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='برند')

    english_title = models.CharField(max_length=255, null=True, blank=True, verbose_name='عنوان انگلیسی')
    short_description = models.TextField(null=True, blank=True, verbose_name='توضیح کوتاه')
    description = models.TextField(verbose_name='توضیحات کامل')

    expert_reviewer = models.CharField(max_length=255, null=True, blank=True, verbose_name='بررسی‌کننده محصول (E-E-A-T)')
    key_takeaways = JSONField(schema=STRING_LIST_SCHEMA, null=True, blank=True, verbose_name='ویژگی‌های کلیدی (GEO)')
    citations = JSONField(schema=STRING_LIST_SCHEMA, null=True, blank=True, verbose_name='منابع کاتالوگ (Citations)')

    base_price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name='قیمت پایه (تکی)')
    base_inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی پایه')
    weight = models.PositiveIntegerField(default=500, verbose_name='وزن (گرم)')
    volume = models.PositiveIntegerField(default=1000, verbose_name='حجم بسته (سانتی‌متر مکعب)')
    favorites = models.ManyToManyField(User, through='ProductFavorite', related_name='favorite_products', blank=True, verbose_name='علاقه‌مندی‌ها')

    special_discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name='درصد تخفیف شگفت‌انگیز')
    special_offer_end = models.DateTimeField(null=True, blank=True, verbose_name='زمان پایان شگفت‌انگیز')

    is_wholesale = models.BooleanField(default=False, verbose_name='قابلیت فروش عمده دارد؟')
    wholesale_min_quantity = models.PositiveIntegerField(default=10, verbose_name='حداقل تعداد برای خرید عمده')
    wholesale_base_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='قیمت پایه عمده')

    sold_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], verbose_name='میانگین امتیاز')

    is_variable = models.BooleanField(default=False, verbose_name='محصول متغیر است؟')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    objects = ProductManager()

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        indexes = [
            models.Index(fields=['slug', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['base_price', 'is_active']),
            models.Index(fields=['special_discount_percent', 'special_offer_end']),
            models.Index(fields=['created_at']),
        ]

    def clean(self) -> None:
        """Enforces model level validation for admin usage."""
        super().clean()
        if self.is_wholesale:
            if not self.wholesale_min_quantity or self.wholesale_min_quantity < 2:
                raise ValidationError({"wholesale_min_quantity": "برای فروش عمده، حداقل تعداد باید بیشتر از ۱ باشد."})
            if self.wholesale_base_price is None:
                raise ValidationError({"wholesale_base_price": "برای فروش عمده، تعیین قیمت پایه عمده الزامی است."})
            if self.base_price is not None and self.wholesale_base_price >= self.base_price:
                raise ValidationError({"wholesale_base_price": "قیمت عمده باید کمتر از قیمت پایه باشد."})

    def __str__(self) -> str:
        return str(self.title)

    @property
    def is_special_offer_active(self) -> bool:
        """Checks if special offer is valid."""
        if self.special_discount_percent > 0 and self.special_offer_end:
            return self.special_offer_end > timezone.now()
        return False

    @property
    def final_price(self) -> int:
        """Calculates effective selling price accounting for active special discounts."""
        price = int(self.base_price or 0)
        if self.is_special_offer_active and self.special_discount_percent > 0:
            discount = (Decimal(price) * Decimal(self.special_discount_percent)) / Decimal(100)
            return max(0, int(Decimal(price) - discount))
        return price

    def get_absolute_url(self) -> str:
        return f"/product/{self.slug}"

    def generate_json_ld(self) -> Dict[str, Any]:
        """Generates schema.org structured data for SEO, AEO, and GEO without N+1 queries."""
        if self.json_ld and isinstance(self.json_ld, dict) and self.json_ld.get("@type"):
            return self.json_ld

        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        site_name: str = getattr(settings, 'SITE_NAME', 'ارک کالا')
        product_url: str = f"{frontend_domain}/product/{self.slug}"

        # Sort gallery so is_main=True is always the first image in JSON-LD
        gallery_items = sorted(list(self.gallery.all()), key=lambda x: not getattr(x, 'is_main', False))
        variants_list = list(self.variants.all())

        approved_comments = getattr(self, 'approved_comments', None)
        if approved_comments is None:
            approved_comments = list(self.comments.filter(is_approved=True).select_related('user')[:10])

        approved_questions = getattr(self, 'approved_questions', None)
        if approved_questions is None:
            approved_questions = list(self.questions.filter(is_approved=True))

        in_stock = self.base_inventory > 0 or any(v.inventory > 0 for v in variants_list)
        effective_price = self.final_price

        offer_data: Dict[str, Any] = {
            "@type": "Offer",
            "url": product_url,
            "priceCurrency": "IRT",
            "price": str(effective_price),
            "availability": "https://schema.org/InStock" if in_stock else "https://schema.org/OutOfStock",
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {
                "@type": "Organization",
                "name": site_name,
                "url": frontend_domain,
            },
        }

        if self.is_special_offer_active and self.special_offer_end:
            offer_data["priceValidUntil"] = self.special_offer_end.strftime("%Y-%m-%d")

        if self.is_variable and variants_list:
            variant_prices = [int(v.price) for v in variants_list if v.price and v.price > 0]
            if variant_prices:
                offer_data = {
                    "@type": "AggregateOffer",
                    "url": product_url,
                    "priceCurrency": "IRT",
                    "lowPrice": str(min(variant_prices)),
                    "highPrice": str(max(variant_prices)),
                    "offerCount": str(len(variant_prices)),
                    "availability": "https://schema.org/InStock" if in_stock else "https://schema.org/OutOfStock",
                }

        clean_desc = (
            self.meta_description
            or self.short_description
            or strip_tags(self.description or "")[:300]
            or self.title
        )

        product_schema: Dict[str, Any] = {
            "@type": "Product",
            "@id": f"{product_url}#product",
            "name": self.title,
            "description": clean_desc,
            "sku": str(self.uuid),
            "mpn": str(self.uuid)[:8].upper(),
            "url": product_url,
            "brand": {
                "@type": "Brand",
                "name": self.brand.title if self.brand else site_name,
            },
            "offers": offer_data,
        }

        if self.english_title:
            product_schema["alternateName"] = self.english_title

        image_urls = [f"{frontend_domain}{img.image.url}" for img in gallery_items if getattr(img, 'image', None)]
        if image_urls:
            product_schema["image"] = image_urls

        additional_properties: List[Dict[str, Any]] = []
        if self.key_takeaways and isinstance(self.key_takeaways, list):
            for idx, takeaway in enumerate(self.key_takeaways, start=1):
                if takeaway:
                    additional_properties.append({
                        "@type": "PropertyValue",
                        "name": f"ویژگی کلیدی {idx}",
                        "value": str(takeaway),
                    })
        if self.weight:
            additional_properties.append({
                "@type": "PropertyValue",
                "name": "وزن",
                "value": f"{self.weight} گرم",
            })
        if additional_properties:
            product_schema["additionalProperty"] = additional_properties

        if self.expert_reviewer:
            product_schema["reviewedBy"] = {
                "@type": "Person",
                "name": self.expert_reviewer,
            }

        if self.citations and isinstance(self.citations, list):
            product_schema["citation"] = [str(c) for c in self.citations if c]

        if getattr(self, 'average_rating', 0) > 0 and approved_comments:
            product_schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(round(self.average_rating, 1)),
                "reviewCount": str(len(approved_comments)),
                "bestRating": "5",
                "worstRating": "1",
            }
            product_schema["review"] = [
                {
                    "@type": "Review",
                    "author": {
                        "@type": "Person",
                        "name": (c.user.get_full_name() if c.user and c.user.get_full_name() else "کاربر خریدار"),
                    },
                    "datePublished": c.created_at.strftime("%Y-%m-%d") if c.created_at else "",
                    "reviewBody": c.body,
                    "reviewRating": {
                        "@type": "Rating",
                        "ratingValue": str(c.rating),
                        "bestRating": "5",
                        "worstRating": "1",
                    },
                }
                for c in approved_comments[:5]
            ]

        product_schema["speakable"] = {
            "@type": "SpeakableSpecification",
            "cssSelector": ["h1", ".product-short-description", ".key-takeaways-list"],
        }

        graph: List[Dict[str, Any]] = [product_schema]

        answered_questions = [
            q for q in approved_questions
            if getattr(q, 'answer_text', None) and str(q.answer_text).strip()
        ]
        if answered_questions:
            graph.append({
                "@type": "FAQPage",
                "@id": f"{product_url}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q.text,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": q.answer_text,
                        },
                    }
                    for q in answered_questions
                ],
            })

        if getattr(self, 'category', None):
            graph.append({
                "@type": "BreadcrumbList",
                "@id": f"{product_url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "خانه", "item": f"{frontend_domain}/"},
                    {"@type": "ListItem", "position": 2, "name": "فروشگاه", "item": f"{frontend_domain}/shop"},
                    {"@type": "ListItem", "position": 3, "name": self.category.title, "item": f"{frontend_domain}/category/{self.category.slug}"},
                    {"@type": "ListItem", "position": 4, "name": self.title, "item": product_url},
                ],
            })

        return {"@context": "https://schema.org", "@graph": graph}


class ProductFavorite(UUIDBaseModel, TimeStampMixin):
    """Explicit Many-To-Many relationship for optimized favorite queries."""
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='favorited_by_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_product_favorites')

    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        unique_together = ('product', 'user')
        indexes = [models.Index(fields=['user', 'product'])]


class ProductGallery(UUIDBaseModel):
    """Images for the product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery', verbose_name='محصول')
    image = models.ImageField(upload_to='products/gallery/', verbose_name='تصویر')
    image_alt = models.CharField(max_length=255, null=True, blank=True, verbose_name='متن جایگزین تصویر (Alt)')
    is_main = models.BooleanField(default=False, verbose_name='تصویر اصلی')

    class Meta:
        verbose_name = 'گالری تصویر محصول'
        verbose_name_plural = 'گالری تصاویر محصولات'
        indexes = [models.Index(fields=['product', 'is_main'])]


class ProductVideo(UUIDBaseModel):
    """Videos for the product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos', verbose_name='محصول')
    video_file = models.FileField(upload_to='products/videos/', verbose_name='فایل ویدیو', validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'webm', 'avi'])])
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='عنوان ویدیو')

    class Meta:
        verbose_name = 'ویدیو محصول'
        verbose_name_plural = 'ویدیوهای محصول'
        ordering = []


class ProductVariant(UUIDBaseModel, TimeStampMixin):
    """Product variations."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='محصول')
    attribute_values = models.ManyToManyField(AttributeValue, related_name='variants', verbose_name='مقادیر ویژگی')
    gallery_image = models.ForeignKey(ProductGallery, on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_variants', verbose_name='تصویر مرتبط از گالری')
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='قیمت تکی')
    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی')
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='قیمت عمده')

    class Meta:
        verbose_name = 'تنوع محصول'
        verbose_name_plural = 'تنوع محصولات'
        indexes = [
            models.Index(fields=['product', 'price']),
            models.Index(fields=['inventory']),
        ]


class PriceHistory(UUIDBaseModel):
    """Historical records of price changes."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history', verbose_name='محصول')
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='قیمت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'تاریخچه قیمت'
        verbose_name_plural = 'تاریخچه قیمت‌ها'
        ordering = ['created_at']
        indexes = [models.Index(fields=['product', 'created_at'])]