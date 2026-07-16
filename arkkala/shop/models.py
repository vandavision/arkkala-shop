"""
Shop Models including Category, Brand, Product, Variants, Images, Videos, and Comments.
Strictly optimized for SEO, AEO (Answer Engine Optimization), and GEO.
"""
from typing import Dict, Any, List
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.conf import settings

from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin, ProductDetailJsonLdMixin

try:
    from django_jsonform.models.fields import JSONField
except ImportError:
    JSONField = models.JSONField

User = get_user_model()

STRING_LIST_SCHEMA: Dict[str, Any] = {
    'type': 'array',
    'items': {'type': 'string'}
}


class Category(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """Product Category Model."""
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('دسته بندی پدر')
    )
    image = models.ImageField(upload_to='categories/images/', null=True, blank=True, verbose_name=_('تصویر'))
    image_alt = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('متن جایگزین تصویر (Alt)'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('دسته بندی')
        verbose_name_plural = _('دسته بندی ها')

    def __str__(self) -> str:
        return self.title


class Brand(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """Product Brand Model."""
    logo = models.ImageField(upload_to='brands/logos/', null=True, blank=True, verbose_name=_('لوگو'))
    logo_alt = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('متن جایگزین لوگو (Alt)'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('برند')
        verbose_name_plural = _('برند ها')

    def __str__(self) -> str:
        return self.title


class Attribute(UUIDBaseModel, TimeStampMixin, TitleSlugMixin):
    """Product Attribute Key (e.g., Color, Size)."""
    class Meta:
        verbose_name = _('ویژگی')
        verbose_name_plural = _('ویژگی ها')

    def __str__(self) -> str:
        return self.title


class AttributeValue(UUIDBaseModel):
    """Product Attribute Value (e.g., Red, XL)."""
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name=_('ویژگی'))
    value = models.CharField(max_length=255, verbose_name=_('مقدار'))

    class Meta:
        verbose_name = _('مقدار ویژگی')
        verbose_name_plural = _('مقادیر ویژگی')

    def __str__(self) -> str:
        return f"{self.attribute.title}: {self.value}"


class Product(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin, ProductDetailJsonLdMixin):
    """Main Product Model with SEO, AEO, and GEO validations."""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name=_('دسته بندی'))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_('برند'))

    english_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('عنوان انگلیسی'))
    short_description = models.TextField(null=True, blank=True, verbose_name=_('توضیح کوتاه'))
    description = models.TextField(verbose_name=_('توضیحات کامل'))

    # --- GEO (Generative Engine Optimization) Fields ---
    expert_reviewer = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('بررسی‌کننده محصول (E-E-A-T)'), help_text=_('مفید برای محصولات تخصصی، پزشکی یا دیجیتال'))
    key_takeaways = JSONField(schema=STRING_LIST_SCHEMA, null=True, blank=True, verbose_name=_('ویژگی‌های کلیدی (GEO)'), help_text=_('بهترین ویژگی‌ها به صورت بولت‌وار برای هوش مصنوعی.'))
    citations = JSONField(schema=STRING_LIST_SCHEMA, null=True, blank=True, verbose_name=_('منابع کاتالوگ (Citations)'), help_text=_('ارجاعات به وب‌سایت سازنده اصلی.'))

    # --- Pricing & Inventory ---
    base_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('قیمت پایه (تکی)'))
    base_inventory = models.PositiveIntegerField(default=0, verbose_name=_('موجودی پایه'))

    weight = models.PositiveIntegerField(default=500, verbose_name=_('وزن (گرم)'), help_text=_('جهت محاسبه دقیق هزینه پستی'))
    volume = models.PositiveIntegerField(default=1000, verbose_name=_('حجم بسته (سانتی‌متر مکعب)'))
    favorites = models.ManyToManyField(User, related_name='favorite_products', blank=True, verbose_name=_('علاقه‌مندی‌ها'))

    special_discount_percent = models.PositiveIntegerField(default=0, verbose_name=_('درصد تخفیف شگفت‌انگیز'))
    special_offer_end = models.DateTimeField(null=True, blank=True, verbose_name=_('زمان پایان شگفت‌انگیز'))

    is_wholesale = models.BooleanField(default=False, verbose_name=_('قابلیت فروش عمده دارد؟'))
    wholesale_min_quantity = models.PositiveIntegerField(default=10, verbose_name=_('حداقل تعداد برای خرید عمده'), help_text=_("در صورت خرید بیشتر از این تعداد، قیمت عمده محاسبه می‌شود."))
    wholesale_base_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name=_('قیمت پایه عمده'))

    sold_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد فروش'))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد بازدید'))
    average_rating = models.FloatField(default=0.0, verbose_name=_('میانگین امتیاز'))

    is_variable = models.BooleanField(default=False, verbose_name=_('محصول متغیر است؟'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('محصول')
        verbose_name_plural = _('محصولات')

    def __str__(self) -> str:
        return self.title

    @property
    def is_special_offer_active(self) -> bool:
        """Check if the special offer is currently active."""
        if self.special_discount_percent > 0 and self.special_offer_end:
            return self.special_offer_end > timezone.now()
        return False
    
    def generate_json_ld(self) -> Dict[str, Any]:
        """
        Generates comprehensive JSON-LD including Product Schema, BreadcrumbList,
        FAQPage (dynamically generated from approved questions for AEO), and E-E-A-T (GEO).
        """
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        product_url: str = f"{frontend_domain}/product/{self.slug}/"
        
        main_img = self.gallery.filter(is_main=True).first() or self.gallery.first()
        
        product_schema = {
            "@type": "Product",
            "name": self.title,
            "description": self.meta_description or self.short_description or self.title,
            "sku": str(self.sku) if hasattr(self, 'sku') else str(self.uuid),
            "brand": {
                "@type": "Brand",
                "name": self.brand.title if self.brand else getattr(settings, 'SITE_NAME', 'ارک کالا')
            },
            "offers": {
                "@type": "Offer",
                "url": product_url,
                "priceCurrency": "IRT",
                "price": str(self.base_price),
                "availability": "https://schema.org/InStock" if (self.base_inventory > 0 or self.variants.filter(inventory__gt=0).exists()) else "https://schema.org/OutOfStock",
                "itemCondition": "https://schema.org/NewCondition"
            }
        }

        # ONLY append image if a valid URL exists to prevent schema validation failure
        if main_img and main_img.image:
            product_schema["image"] = {
                "@type": "ImageObject",
                "url": f"{frontend_domain}{main_img.image.url}",
                "description": main_img.image_alt or self.title
            }

        json_ld: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@graph": [product_schema]
        }

        # GEO: Reviews & E-E-A-T
        if self.expert_reviewer:
            json_ld["@graph"][0]["reviewedBy"] = {
                "@type": "Person",
                "name": self.expert_reviewer
            }
        
        if self.citations:
            json_ld["@graph"][0]["citation"] = self.citations

        if getattr(self, 'average_rating', 0) > 0 and self.comments.filter(is_approved=True).exists():
            json_ld["@graph"][0]["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(round(self.average_rating, 1)),
                "reviewCount": str(self.comments.filter(is_approved=True).count())
            }

        # AEO: Dynamic FAQ generation from Questions
        answered_questions = self.questions.filter(is_approved=True).exclude(answer_text__isnull=True).exclude(answer_text__exact='')
        if answered_questions.exists():
            faq_items = []
            for q in answered_questions:
                faq_items.append({
                    "@type": "Question",
                    "name": q.text,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": q.answer_text
                    }
                })
            json_ld["@graph"].append({
                "@type": "FAQPage",
                "mainEntity": faq_items
            })

        # SEO: Breadcrumbs
        if getattr(self, 'category', None):
            breadcrumbs: List[Dict[str, Any]] = [
                {"@type": "ListItem", "position": 1, "name": "خانه", "item": f"{frontend_domain}/"},
                {"@type": "ListItem", "position": 2, "name": "فروشگاه", "item": f"{frontend_domain}/shop/"},
                {"@type": "ListItem", "position": 3, "name": self.category.title, "item": f"{frontend_domain}/category/{self.category.slug}/"},
                {"@type": "ListItem", "position": 4, "name": self.title, "item": product_url}
            ]
            json_ld["@graph"].append({
                "@type": "BreadcrumbList",
                "itemListElement": breadcrumbs
            })

        return json_ld


class ProductGallery(UUIDBaseModel):
    """Product Images."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery', verbose_name=_('محصول'))
    image = models.ImageField(upload_to='products/gallery/', verbose_name=_('تصویر'))
    image_alt = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('متن جایگزین تصویر (Alt)'), help_text=_('حیاتی برای سئوی تصاویر کالا'))
    is_main = models.BooleanField(default=False, verbose_name=_('تصویر اصلی'))

    class Meta:
        verbose_name = _('گالری تصویر محصول')
        verbose_name_plural = _('گالری تصاویر محصولات')


class ProductVideo(UUIDBaseModel):
    """Product Videos."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos', verbose_name=_('محصول'))
    video_file = models.FileField(
        upload_to='products/videos/',
        verbose_name=_('فایل ویدیو'),
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'webm', 'avi'])]
    )
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('عنوان ویدیو'))

    class Meta:
        verbose_name = _('ویدیو محصول')
        verbose_name_plural = _('ویدیوهای محصول')


class ProductVariant(UUIDBaseModel, TimeStampMixin):
    """Product Variants for Variable Products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name=_('محصول'))
    attribute_values = models.ManyToManyField(AttributeValue, related_name='variants', verbose_name=_('مقادیر ویژگی'))

    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('قیمت تکی'))
    inventory = models.PositiveIntegerField(default=0, verbose_name=_('موجودی'))
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name=_('قیمت عمده'))

    class Meta:
        verbose_name = _('تنوع محصول')
        verbose_name_plural = _('تنوع محصولات')


class Comment(UUIDBaseModel, TimeStampMixin):
    """Product Comments & Ratings."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name=_('محصول'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('کاربر'))
    body = models.TextField(verbose_name=_('متن نظر'))
    rating = models.PositiveSmallIntegerField(default=5, verbose_name=_('امتیاز'))
    is_approved = models.BooleanField(default=False, verbose_name=_('تایید شده'))

    class Meta:
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')


class Question(UUIDBaseModel, TimeStampMixin):
    """Represents a user or guest question. Serves as dynamic AEO base."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions', verbose_name=_('محصول'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('کاربر ثبت‌نام شده'))
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('نام نویسنده مهمان'))
    text = models.TextField(verbose_name=_('متن پرسش'))
    answer_text = models.TextField(null=True, blank=True, verbose_name=_('متن پاسخ ادمین'))
    is_approved = models.BooleanField(default=False, verbose_name=_('تایید شده برای نمایش'))

    class Meta:
        verbose_name = _('پرسش و پاسخ')
        verbose_name_plural = _('پرسش‌ها و پاسخ‌ها')
        ordering = ['-created_at']

    def __str__(self) -> str:
        author = self.user.get_full_name() if self.user else (self.name or _('کاربر مهمان'))
        return f"Question on {self.product.title} by {author}"


class PriceHistory(UUIDBaseModel):
    """Tracks the price changes of a product over time for the price chart."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history', verbose_name=_('محصول'))
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_('قیمت'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    class Meta:
        verbose_name = _('تاریخچه قیمت')
        verbose_name_plural = _('تاریخچه قیمت‌ها')
        ordering = ['created_at']

    def __str__(self) -> str:
        return f"{self.product.title} - {self.price} - {self.created_at.strftime('%Y-%m-%d')}"