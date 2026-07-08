"""
Shop Models including Category, Brand, Product, Variants, Images, Videos, and Comments.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from typing import Dict, Any, List
from django.conf import settings
from platform_tools.mixins.models.base import UUIDBaseModel, TimeStampMixin, TitleSlugMixin
from platform_seo.models.mixins.seo import SEOMixin, ProductDetailJsonLdMixin

User = get_user_model()


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
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('دسته بندی')
        verbose_name_plural = _('دسته بندی ها')


class Brand(UUIDBaseModel, TimeStampMixin, TitleSlugMixin, SEOMixin):
    """Product Brand Model."""
    logo = models.ImageField(upload_to='brands/logos/', null=True, blank=True, verbose_name=_('لوگو'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('برند')
        verbose_name_plural = _('برند ها')


class Attribute(UUIDBaseModel, TimeStampMixin, TitleSlugMixin):
    """Product Attribute Key (e.g., Color, Size)."""
    class Meta:
        verbose_name = _('ویژگی')
        verbose_name_plural = _('ویژگی ها')


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
    """Main Product Model."""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name=_('دسته بندی'))
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name=_('برند'))

    english_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('عنوان انگلیسی'))
    short_description = models.TextField(null=True, blank=True, verbose_name=_('توضیح کوتاه'))
    description = models.TextField(verbose_name=_('توضیحات کامل'))

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

    @property
    def is_special_offer_active(self) -> bool:
        """
        Check if the special offer is currently active.
        
        Returns:
            bool: True if active, False otherwise.
        """
        if self.special_discount_percent > 0 and self.special_offer_end:
            return self.special_offer_end > timezone.now()
        return False
    
    def generate_json_ld(self) -> Dict[str, Any]:
        """
        Generates comprehensive JSON-LD including Product Schema and BreadcrumbList.
        Designed specifically for Headless SEO.
        
        Returns:
            Dict[str, Any]: A dictionary containing the structured JSON-LD data.
        """
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        product_url: str = f"{frontend_domain}/product/{self.slug}/"
        
        json_ld: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Product",
                    "name": self.title,
                    "image": [self.gallery.first().image.url if self.gallery.exists() else ""],
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
                        "availability": "https://schema.org/InStock" if self.base_inventory > 0 else "https://schema.org/OutOfStock",
                        "itemCondition": "https://schema.org/NewCondition"
                    }
                }
            ]
        }

        if getattr(self, 'average_rating', 0) > 0 and self.comments.filter(is_approved=True).exists():
            json_ld["@graph"][0]["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(round(self.average_rating, 1)),
                "reviewCount": str(self.comments.filter(is_approved=True).count())
            }

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
        ordering = ['created_at'] if hasattr(UUIDBaseModel, 'created_at') else []


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
    """Represents a user or guest question about a specific product, along with its answer."""
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