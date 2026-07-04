"""
Shop Models including Category, Brand, Product, Variants, and Comments.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

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


class ProductGallery(UUIDBaseModel):
    """Product Images."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery', verbose_name=_('محصول'))
    image = models.ImageField(upload_to='products/gallery/', verbose_name=_('تصویر'))
    is_main = models.BooleanField(default=False, verbose_name=_('تصویر اصلی'))

    class Meta:
        verbose_name = _('گالری محصول')
        verbose_name_plural = _('گالری محصولات')


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