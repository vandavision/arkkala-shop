import json
import ssl
import urllib.request
from typing import Any, Dict, List, Optional

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop.models import (
    Attribute, Brand, Category, Product, ProductGallery, ProductVideo
)

FALLBACK_DATA: List[Dict[str, Any]] = [
    {
        "title": "گوشی موبایل اپل مدل iPhone 15 Pro Max",
        "en_title": "Apple iPhone 15 Pro Max Smartphone",
        "price": 1200,
        "description": "جدیدترین پرچمدار اپل با بدنه تیتانیومی، دوربین بسیار پیشرفته ۴۸ مگاپیکسلی و پردازنده قدرتمند A17 Pro. این محصول با طراحی ارگونومیک و صفحه نمایش Super Retina XDR بهترین تجربه کاربری را ارائه می‌دهد.",
        "category": "کالای دیجیتال",
        "image": "https://picsum.photos/800/800?random=1",
        "rating": {"rate": 4.8, "count": 120}
    },
    {
        "title": "لپ‌تاپ گیمینگ ایسوس مدل ROG Strix G16",
        "en_title": "ASUS ROG Strix G16 Gaming Laptop",
        "price": 1500,
        "description": "لپ‌تاپ قدرتمند مخصوص بازی با پردازنده نسل ۱۳ اینتل Core i7 و گرافیک فوق‌العاده RTX 4060. مناسب برای رندرینگ، برنامه‌نویسی و اجرای جدیدترین بازی‌ها با بالاترین کیفیت.",
        "category": "لپ‌تاپ",
        "image": "https://picsum.photos/800/800?random=2",
        "rating": {"rate": 4.5, "count": 85}
    },
    {
        "title": "ساعت هوشمند سامسونگ مدل Galaxy Watch 6",
        "en_title": "Samsung Galaxy Watch 6 Smartwatch",
        "price": 300,
        "description": "ساعت هوشمند پیشرفته با قابلیت پیگیری دقیق وضعیت سلامتی، سنسور ضربان قلب، سنجش اکسیژن خون و صفحه نمایش Super AMOLED. طراحی زیبا و باتری با دوام.",
        "category": "گجت‌های هوشمند",
        "image": "https://picsum.photos/800/800?random=3",
        "rating": {"rate": 4.2, "count": 200}
    }
]

DUMMY_IMAGE_BYTES: bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

class Command(BaseCommand):
    """Management command to seed the database robustly with fallbacks and full SEO data."""
    help: str = "Clears the database and seeds products using fallback data with complete SEO."
    VIDEO_URL: str = "https://www.w3schools.com/html/mov_bbb.mp4"
    SITE_NAME: str = "ارک کالا"

    def handle(self, *args: Any, **options: Any) -> None:
        """Executes the population script operations."""
        self.stdout.write("Starting database cleanup...")
        self.clear_database()
        
        self.stdout.write("Seeding products with complete SEO data...")
        self.seed_products(FALLBACK_DATA)
        
        self.stdout.write(self.style.SUCCESS("Database seeded successfully with full SEO attributes."))

    def clear_database(self) -> None:
        """Purges old application state natively."""
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Attribute.objects.all().delete()

    def download_file(self, url: str, filename: str, is_image: bool = True) -> Optional[ContentFile]:
        """Secures media byte chunks downloading and streaming natively."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                return ContentFile(response.read(), name=filename)
        except Exception:
            if is_image:
                return ContentFile(DUMMY_IMAGE_BYTES, name=filename if filename.endswith('.png') else f"{filename}.png")
            return None

    def get_or_create_category(self, title: str) -> Category:
        """Establishes or returns a localized Category setup element with SEO."""
        slug_val = slugify(title, allow_unicode=True)
        category, created = Category.objects.get_or_create(
            title=title,
            defaults={
                'slug': slug_val,
                'keywords': ["دسته بندی", title, "خرید", "فروشگاه اینترنتی", self.SITE_NAME],
                'meta_description': f"خرید و قیمت انواع {title} در فروشگاه {self.SITE_NAME} با تضمین اصالت و کیفیت.",
                'og_title': f"خرید {title} | {self.SITE_NAME}",
                'og_description': f"جدیدترین محصولات {title} را با بهترین قیمت از {self.SITE_NAME} بخرید.",
                'og_type': "website",
                'og_site_name': self.SITE_NAME,
                'twitter_card': "summary_large_image",
                'twitter_site': "@arkkala"
            }
        )
        return category

    def get_or_create_brand(self, title: str) -> Brand:
        """Establishes or returns a localized Brand setup element with SEO."""
        slug_val = slugify(title, allow_unicode=True)
        brand, created = Brand.objects.get_or_create(
            title=title,
            defaults={
                'slug': slug_val,
                'keywords': ["برند", title, "نمایندگی", "محصولات", self.SITE_NAME],
                'meta_description': f"خرید محصولات برند {title} با تضمین بهترین قیمت و گارانتی اصالت کالا در {self.SITE_NAME}.",
                'og_title': f"محصولات برند {title} | {self.SITE_NAME}",
                'og_description': f"لیست کامل محصولات برند {title} را همراه با تخفیف‌های ویژه مشاهده کنید.",
                'og_type': "website",
                'og_site_name': self.SITE_NAME,
                'twitter_card': "summary_large_image",
                'twitter_site': "@arkkala"
            }
        )
        return brand

    def seed_products(self, data: List[Dict[str, Any]]) -> None:
        """Parses DTO arrays and invokes Domain model structures natively."""
        brand = self.get_or_create_brand("برند اصلی")
        
        for index, item in enumerate(data):
            raw_title = item.get("title", "")[:250]
            en_title = item.get("en_title", "")[:250]
            desc = item.get("description", "")
            category = self.get_or_create_category(item.get("category", "عمومی"))
            price_irt: int = int(float(item.get("price", 0)) * 50000)
            
            product = Product.objects.create(
                category=category,
                brand=brand,
                title=raw_title,
                english_title=en_title,
                slug=slugify(en_title, allow_unicode=True)[:250] or f"product-{index}",
                short_description=desc[:150] + "...",
                description=desc,
                base_price=price_irt,
                base_inventory=150,
                weight=500,
                volume=1000,
                is_active=True,
                average_rating=item.get("rating", {}).get("rate", 0.0),
                view_count=item.get("rating", {}).get("count", 0),
                
                # --- SEO Fields ---
                keywords=["خرید آنلاین", raw_title, category.title, brand.title, "ارزان‌ترین قیمت", "گارانتی اصلی"],
                meta_description=f"بررسی تخصصی و خرید {raw_title} با بهترین قیمت در {self.SITE_NAME}. دارای ضمانت اصالت کالا، ارسال سریع و گارانتی معتبر شرکتی.",
                og_title=f"{raw_title} | نقد و بررسی و خرید",
                og_type="product",
                og_description=f"مشخصات فنی و قیمت روز {raw_title} را در {self.SITE_NAME} ببینید. خرید امن و ارسال به سراسر کشور.",
                og_site_name=self.SITE_NAME,
                og_locale="fa_IR",
                twitter_card="summary_large_image",
                twitter_site="@arkkala",
                twitter_creator="@arkkala_admin",
                
                # --- E-E-A-T (Generative AI Fields) ---
                expert_reviewer="تیم بررسی فنی ارک کالا",
                key_takeaways=["کیفیت ساخت فوق‌العاده", "ارزش خرید بالا در برابر قیمت", "پشتیبانی و قطعات اورجینال"],
                citations=["کاتالوگ رسمی شرکت سازنده", "تست‌های عملیاتی آزمایشگاه ارک کالا"]
            )
            
            image_url: Optional[str] = item.get("image")
            if image_url:
                filename = f"product_{product.uuid}.png"
                image_file = self.download_file(image_url, filename, is_image=True)
                if image_file:
                    ProductGallery.objects.create(
                        product=product,
                        image=image_file,
                        image_alt=f"تصویر اورجینال {product.title}",
                        is_main=True
                    )
            
            if index % 2 == 0:
                video_file = self.download_file(self.VIDEO_URL, f"video_{product.uuid}.mp4", is_image=False)
                if video_file:
                    ProductVideo.objects.create(
                        product=product,
                        video_file=video_file,
                        title=f"جعبه‌گشایی و بررسی ویدیویی {product.title}"
                    )
            
            self.stdout.write(f"✓ Created securely with Full SEO payload: {product.title}")