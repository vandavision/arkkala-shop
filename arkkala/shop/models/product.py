# shop/models/product.py
from typing import Dict, Any, List
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.conf import settings
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin, ProductDetailJsonLdMixin
from shop.managers import ProductManager
from .category import Category
from .brand import Brand
from .attribute import AttributeValue

try:
    from django_jsonform.models.fields import JSONField
except ImportError:
    JSONField = models.JSONField

User = get_user_model()

STRING_LIST_SCHEMA: Dict[str, Any] = {'type': 'array', 'items': {'type': 'string'}}


class Product(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin, ProductDetailJsonLdMixin):
    """Main Product Model with SEO, AEO, and GEO validations."""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name='دسته بندی')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='برند')

    english_title = models.CharField(max_length=255, null=True, blank=True, verbose_name='عنوان انگلیسی')
    short_description = models.TextField(null=True, blank=True, verbose_name='توضیح کوتاه')
    description = models.TextField(verbose_name='توضیحات کامل')

    expert_reviewer = models.CharField(max_length=255, null=True, blank=True, verbose_name='بررسی‌کننده محصول (E-E-A-T)')
    key_takeaways = JSONField(schema=STRING_LIST_SCHEMA, null=True, blank=True, verbose_name='ویژگی‌های کلیدی (GEO)')
    citations = JSONField(schema=STRING_LIST_SCHEMA, null=True, blank=True, verbose_name='منابع کاتالوگ (Citations)')

    base_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='قیمت پایه (تکی)')
    base_inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی پایه')
    weight = models.PositiveIntegerField(default=500, verbose_name='وزن (گرم)')
    volume = models.PositiveIntegerField(default=1000, verbose_name='حجم بسته (سانتی‌متر مکعب)')
    favorites = models.ManyToManyField(User, related_name='favorite_products', blank=True, verbose_name='علاقه‌مندی‌ها')

    special_discount_percent = models.PositiveIntegerField(default=0, verbose_name='درصد تخفیف شگفت‌انگیز')
    special_offer_end = models.DateTimeField(null=True, blank=True, verbose_name='زمان پایان شگفت‌انگیز')

    is_wholesale = models.BooleanField(default=False, verbose_name='قابلیت فروش عمده دارد؟')
    wholesale_min_quantity = models.PositiveIntegerField(default=10, verbose_name='حداقل تعداد برای خرید عمده')
    wholesale_base_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='قیمت پایه عمده')

    sold_count = models.PositiveIntegerField(default=0, verbose_name='تعداد فروش')
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    average_rating = models.FloatField(default=0.0, verbose_name='میانگین امتیاز')

    is_variable = models.BooleanField(default=False, verbose_name='محصول متغیر است؟')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    objects = ProductManager()

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

    def __str__(self) -> str:
        return str(self.title)

    @property
    def is_special_offer_active(self) -> bool:
        if self.special_discount_percent > 0 and self.special_offer_end:
            return self.special_offer_end > timezone.now()
        return False

    def generate_json_ld(self) -> Dict[str, Any]:
        """Generates schema.org structured data."""
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        product_url: str = f"{frontend_domain}/product/{self.slug}/"
        main_img = self.gallery.filter(is_main=True).first() or self.gallery.first()

        product_schema = {
            "@type": "Product",
            "name": self.title,
            "description": self.meta_description or self.short_description or self.title,
            "sku": str(getattr(self, 'sku', self.uuid)),
            "brand": {"@type": "Brand", "name": self.brand.title if self.brand else getattr(settings, 'SITE_NAME', 'ارک کالا')},
            "offers": {
                "@type": "Offer",
                "url": product_url,
                "priceCurrency": "IRT",
                "price": str(self.base_price),
                "availability": "https://schema.org/InStock" if (self.base_inventory > 0 or self.variants.filter(inventory__gt=0).exists()) else "https://schema.org/OutOfStock",
                "itemCondition": "https://schema.org/NewCondition"
            }
        }

        if main_img and main_img.image:
            product_schema["image"] = {
                "@type": "ImageObject",
                "url": f"{frontend_domain}{main_img.image.url}",
                "description": main_img.image_alt or self.title
            }

        json_ld: Dict[str, Any] = {"@context": "https://schema.org", "@graph": [product_schema]}

        if self.expert_reviewer:
            json_ld["@graph"][0]["reviewedBy"] = {"@type": "Person", "name": self.expert_reviewer}
        
        if self.citations:
            json_ld["@graph"][0]["citation"] = self.citations

        if getattr(self, 'average_rating', 0) > 0 and self.comments.filter(is_approved=True).exists():
            json_ld["@graph"][0]["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(round(self.average_rating, 1)),
                "reviewCount": str(self.comments.filter(is_approved=True).count())
            }

        answered_questions = self.questions.filter(is_approved=True).exclude(answer_text__isnull=True).exclude(answer_text__exact='')
        if answered_questions.exists():
            json_ld["@graph"].append({
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q.text, "acceptedAnswer": {"@type": "Answer", "text": q.answer_text}} 
                    for q in answered_questions
                ]
            })

        if getattr(self, 'category', None):
            json_ld["@graph"].append({
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "خانه", "item": f"{frontend_domain}/"},
                    {"@type": "ListItem", "position": 2, "name": "فروشگاه", "item": f"{frontend_domain}/shop/"},
                    {"@type": "ListItem", "position": 3, "name": self.category.title, "item": f"{frontend_domain}/category/{self.category.slug}/"},
                    {"@type": "ListItem", "position": 4, "name": self.title, "item": product_url}
                ]
            })

        return json_ld


class ProductGallery(UUIDBaseModel):
    """Product Images."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery', verbose_name='محصول')
    image = models.ImageField(upload_to='products/gallery/', verbose_name='تصویر')
    image_alt = models.CharField(max_length=255, null=True, blank=True, verbose_name='متن جایگزین تصویر (Alt)')
    is_main = models.BooleanField(default=False, verbose_name='تصویر اصلی')

    class Meta:
        verbose_name = 'گالری تصویر محصول'
        verbose_name_plural = 'گالری تصاویر محصولات'


class ProductVideo(UUIDBaseModel):
    """Product Videos."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos', verbose_name='محصول')
    video_file = models.FileField(
        upload_to='products/videos/', verbose_name='فایل ویدیو',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'webm', 'avi'])]
    )
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='عنوان ویدیو')

    class Meta:
        verbose_name = 'ویدیو محصول'
        verbose_name_plural = 'ویدیوهای محصول'


class ProductVariant(UUIDBaseModel, TimeStampMixin):
    """Product Variants for Variable Products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name='محصول')
    attribute_values = models.ManyToManyField(AttributeValue, related_name='variants', verbose_name='مقادیر ویژگی')
    gallery_image = models.ForeignKey(
        ProductGallery, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='linked_variants', verbose_name='تصویر مرتبط از گالری'
    )
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='قیمت تکی')
    inventory = models.PositiveIntegerField(default=0, verbose_name='موجودی')
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name='قیمت عمده')

    class Meta:
        verbose_name = 'تنوع محصول'
        verbose_name_plural = 'تنوع محصولات'


class PriceHistory(UUIDBaseModel):
    """Tracks historical price changes."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history', verbose_name='محصول')
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='قیمت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'تاریخچه قیمت'
        verbose_name_plural = 'تاریخچه قیمت‌ها'
        ordering = ['created_at']