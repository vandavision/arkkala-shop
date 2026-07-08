"""
Seed Data Command for Arkkala E-Commerce.
Populates the database with initial categories, brands, products, blog posts,
and complete Headless SEO configurations (MetaInformation, OpenGraph, Twitter Cards, JSON-LD).
"""
import logging
from typing import Any, Dict, List

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model

from shop.models import Category as ShopCategory, Brand, Product
from blog.models import Category as BlogCategory, Post
from platform_seo.models import MetaInformation, RobotsTxt

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed database with initial data including complete SEO meta parameters for Headless architecture."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(self.style.WARNING("Starting database seeding process..."))

        try:
            with transaction.atomic():
                self._seed_robots_txt()
                self._seed_static_pages_seo()
                self._seed_shop_data()
                self._seed_blog_data()

            self.stdout.write(self.style.SUCCESS("Database seeded successfully with 100% Complete SEO Metadata!"))
        except Exception as e:
            logger.error(f"Seeding failed: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Error during seeding: {e}"))

    def _seed_robots_txt(self) -> None:
        """Seeds the standard Robots.txt."""
        self.stdout.write("Seeding RobotsTxt...")
        RobotsTxt.objects.update_or_create(
            id=1,
            defaults={
                "content": "User-agent: *\nDisallow: /admin/\nDisallow: /checkout/\nAllow: /\n"
            }
        )

    def _seed_static_pages_seo(self) -> None:
        """Seeds MetaInformation for React static routes with complete Schema and OG metadata."""
        self.stdout.write("Seeding Static Pages SEO (MetaInformation)...")
        
        frontend_url: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')

        meta_pages: List[Dict[str, Any]] = [
            {
                "view_name": "HomePage",
                "title": "فروشگاه اینترنتی ارک کالا | بررسی، انتخاب و خرید آنلاین",
                "canonical_url": f"{frontend_url}/",
                "description": "ارک کالا، مرجع تخصصی نقد و بررسی و فروش اینترنتی کالا در ایران. با ضمانت اصالت کالا، ارسال سریع و پشتیبانی ۲۴ ساعته، خریدی مطمئن را تجربه کنید.",
                "keywords": ["فروشگاه اینترنتی", "خرید آنلاین", "خرید موبایل", "خرید لپ تاپ", "ارک کالا"],
                "index_page": True,
                "follow_page_links": True,
                "json_ld": {
                    "@context": "https://schema.org",
                    "@type": "WebPage",
                    "name": "فروشگاه اینترنتی ارک کالا",
                    "url": f"{frontend_url}/",
                    "description": "ارک کالا، مرجع تخصصی نقد و بررسی و فروش اینترنتی کالا در ایران.",
                    "image": f"{frontend_url}/assets/image/logo.png",
                    "mainEntity": {
                        "@type": "Organization",
                        "name": "ارک کالا (Arkkala)",
                        "url": f"{frontend_url}/",
                        "logo": f"{frontend_url}/assets/image/logo.png",
                        "sameAs": ["https://instagram.com/arkkala", "https://twitter.com/arkkala"],
                        "contactPoint": {
                            "@type": "ContactPoint",
                            "telephone": "+982155555555",
                            "contactType": "Customer Support",
                            "areaServed": "IR",
                            "availableLanguage": "Persian"
                        }
                    }
                }
            },
            {
                "view_name": "ShopPage",
                "title": "فروشگاه | تمامی محصولات ارک کالا",
                "canonical_url": f"{frontend_url}/shop/",
                "description": "خرید انواع محصولات دیجیتال، لوازم خانگی و پوشاک با بهترین قیمت در ارک کالا. جستجو و فیلتر پیشرفته محصولات برای تجربه خریدی هوشمندانه.",
                "keywords": ["محصولات ارک کالا", "فروشگاه کالا", "قیمت روز کالا", "خرید اینترنتی کالا"],
                "index_page": True,
                "follow_page_links": True,
                "json_ld": {
                    "@context": "https://schema.org",
                    "@type": "CollectionPage",
                    "name": "فروشگاه تمامی محصولات ارک کالا",
                    "url": f"{frontend_url}/shop/"
                }
            },
            {
                "view_name": "BlogPage",
                "title": "مجله اینترنتی ارک کالا | مقالات و اخبار تکنولوژی",
                "canonical_url": f"{frontend_url}/blog/",
                "description": "جدیدترین اخبار تکنولوژی، نقد و بررسی تخصصی گجت‌ها، و راهنمای جامع خرید محصولات دیجیتال را در مجله اینترنتی ارک کالا مطالعه کنید.",
                "keywords": ["مجله تکنولوژی", "اخبار فناوری", "راهنمای خرید موبایل", "وبلاگ ارک کالا"],
                "index_page": True,
                "follow_page_links": True,
                "json_ld": {
                    "@context": "https://schema.org",
                    "@type": "Blog",
                    "name": "مجله اینترنتی ارک کالا",
                    "url": f"{frontend_url}/blog/",
                    "publisher": {
                        "@type": "Organization",
                        "name": "ارک کالا",
                        "logo": {
                            "@type": "ImageObject",
                            "url": f"{frontend_url}/assets/image/logo.png"
                        }
                    }
                }
            }
        ]

        for page_data in meta_pages:
            MetaInformation.objects.update_or_create(
                view_name=page_data["view_name"],
                defaults=page_data
            )

    def _seed_shop_data(self) -> None:
        """Seeds Brands, Categories, and Products with full SEOMixin parameters."""
        self.stdout.write("Seeding Shop Data (Brands, Categories, Products)...")
        frontend_url: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')

        apple, _ = Brand.objects.update_or_create(title="اپل", defaults={"slug": "apple"})
        samsung, _ = Brand.objects.update_or_create(title="سامسونگ", defaults={"slug": "samsung"})

        digital_cat, _ = ShopCategory.objects.update_or_create(title="کالای دیجیتال", defaults={"slug": "digital"})
        mobile_cat, _ = ShopCategory.objects.update_or_create(title="موبایل", defaults={"slug": "mobile", "parent": digital_cat})

        prod_title = "گوشی موبایل اپل مدل iPhone 15 Pro Max"
        prod_slug = "apple-iphone-15-pro-max"
        
        Product.objects.update_or_create(
            slug=prod_slug,
            defaults={
                "title": prod_title,
                "category": mobile_cat,
                "brand": apple,
                "base_price": 85000000,
                "base_inventory": 15,
                "short_description": "پرچمدار جدید اپل با بدنه تیتانیومی مقاوم، پردازنده فوق سریع و دوربین پریسکوپی ۵ برابری برای عکاسی حرفه‌ای.",
                "description": "گوشی iPhone 15 Pro Max با پردازنده قدرتمند A17 Pro و پورت Type-C روانه بازار شده است. این محصول با کیفیت ساخت بسیار بالا و سیستم عامل روان iOS، تجربه‌ای بی‌نظیر از دنیای دیجیتال را برای شما رقم می‌زند و بهترین انتخاب برای کاربران حرفه‌ای است.",
                "is_active": True,
                
                "meta_description": "خرید گوشی آیفون 15 پرو مکس (iPhone 15 Pro Max) با بهترین قیمت و گارانتی 18 ماهه شرکتی از فروشگاه اینترنتی ارک کالا. ارسال فوری به سراسر کشور.",
                "keywords": ["آیفون 15 پرو مکس", "خرید iphone 15 pro max", "قیمت آیفون 15", "خرید گوشی اپل"],
                
                "og_title": f"خرید و قیمت {prod_title} | ارک کالا",
                "og_type": "product",
                "og_description": "بررسی مشخصات فنی و خرید آیفون 15 پرو مکس با تضمین رجیستری معتبر، گارانتی معتبر و بهترین قیمت در بازار ایران.",
                "og_url": f"{frontend_url}/product/{prod_slug}/",
                "og_site_name": "ارک کالا",
                "og_locale": "fa_IR",
                
                "twitter_card": "summary_large_image",
                "twitter_site": "@arkkala",
                "twitter_creator": "@arkkala_store",
            }
        )

    def _seed_blog_data(self) -> None:
        """Seeds Blog Posts with full SEOMixin parameters."""
        self.stdout.write("Seeding Blog Data (Posts)...")
        frontend_url: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')

        author, _ = User.objects.get_or_create(
            phone_number="09120000000",
            defaults={"first_name": "مدیر", "last_name": "ارشد", "is_staff": True, "is_superuser": True}
        )

        tech_cat, _ = BlogCategory.objects.update_or_create(title="تکنولوژی", defaults={"slug": "technology"})

        post_title = "راهنمای جامع خرید گوشی موبایل در سال ۲۰۲۶"
        post_slug = "smartphone-buying-guide-2026"

        Post.objects.update_or_create(
            slug=post_slug,
            defaults={
                "title": post_title,
                "category": tech_cat,
                "author": author,
                "body": "<p>در این مقاله به بررسی برترین گوشی‌های بازار در بازه‌های قیمتی مختلف می‌پردازیم. انتخاب گوشی مناسب نیازمند شناخت دقیق پردازنده‌ها، کیفیت دوربین، میزان شارژدهی باتری و نیازهای شخصی شما است تا بتوانید بهترین ارزش خرید را تجربه کنید.</p>",
                "short_description": "جامع‌ترین راهنمای خرید اسمارت‌فون، از گوشی‌های اقتصادی تا پرچمداران سال ۲۰۲۶ را در این مطلب تخصصی بخوانید.",
                "read_time": 8,
                "is_published": True,

                "meta_description": "راهنمای خرید بهترین گوشی‌های موبایل در سال ۲۰۲۶. مشاوره تخصصی برای انتخاب اسمارت‌فون بر اساس بودجه و نیاز شما (عمر باتری، دوربین حرفه‌ای، گیمینگ و کاربری روزمره).",
                "keywords": ["راهنمای خرید گوشی", "بهترین گوشی 2026", "خرید موبایل", "مشاوره خرید گوشی", "ارک کالا مگ"],

                "og_title": post_title,
                "og_type": "article",
                "og_description": "قصد خرید گوشی جدید دارید؟ در این مقاله کاربردی تمامی گوشی‌های ارزشمند بازار را زیر ذره‌بین برده‌ایم تا خریدی هوشمندانه داشته باشید.",
                "og_url": f"{frontend_url}/blog/{post_slug}/",
                "og_site_name": "مجله ارک کالا",
                "og_locale": "fa_IR",
                "article_author": "تیم تحریریه ارک کالا",

                "twitter_card": "summary_large_image",
                "twitter_site": "@arkkala_mag",
                "twitter_creator": "@arkkala_mag",
            }
        )