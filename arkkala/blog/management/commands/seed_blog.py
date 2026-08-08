import json
import os
import random
import ssl
import urllib.request
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from blog.models import Category, Comment, Post, Tag

User = get_user_model()

FALLBACK_DATA: List[Dict[str, Any]] = [
    {
        "title": "راهنمای جامع خرید لپ‌تاپ برنامه‌نویسی در سال جاری",
        "body": "برای برنامه‌نویسی نیاز به پردازنده‌های چند هسته‌ای، حداقل ۱۶ گیگابایت رم و حافظه SSD پرسرعت دارید. مک‌بوک‌های اپل و سری ROG ایسوس بهترین گزینه‌ها هستند. همچنین داشتن صفحه نمایش با کیفیت برای جلوگیری از خستگی چشم بسیار حیاتی است.",
        "category": "تکنولوژی",
        "tags": ["لپ‌تاپ", "برنامه‌نویسی", "راهنمای خرید"],
    },
    {
        "title": "آینده هوش مصنوعی و تاثیر آن بر سئو (GEO)",
        "body": "با روی کار آمدن SGE و موتورهای پاسخگو، دیگر بهینه‌سازی سنتی کلمات کلیدی کافی نیست. شما باید روی E-E-A-T و داده‌های ساختاریافته تمرکز کنید. محتوای تولید شده توسط هوش مصنوعی نیاز به بررسی توسط متخصصان واقعی دارد.",
        "category": "سئو و دیجیتال مارکتینگ",
        "tags": ["هوش مصنوعی", "سئو", "دیجیتال مارکتینگ"],
    },
    {
        "title": "معرفی فریم‌ورک جنگو و قابلیت‌های جدید آن",
        "body": "جنگو یک فریم‌ورک قدرتمند پایتون است که سرعت توسعه را به شدت افزایش می‌دهد. معماری MVT و پنل ادمین داخلی آن، این فریم‌ورک را به انتخاب اول بسیاری از استارتاپ‌ها تبدیل کرده است.",
        "category": "توسعه نرم‌افزار",
        "tags": ["پایتون", "جنگو", "توسعه وب"],
    },
    {
        "title": "بررسی تخصصی دوربین‌های پرچمدار جدید",
        "body": "سنسورهای یک اینچی و الگوریتم‌های پردازش تصویر مبتنی بر شبکه عصبی، کیفیت عکاسی با موبایل را به سطح دوربین‌های حرفه‌ای رسانده‌اند.",
        "category": "بررسی محصول",
        "tags": ["موبایل", "عکاسی", "تکنولوژی"],
    },
    {
        "title": "۱۰ عادت روزانه برای افزایش بهره‌وری",
        "body": "مدیریت زمان، تکنیک پومودورو، خواب کافی و دوری از شبکه‌های اجتماعی در ساعات کاری می‌تواند بهره‌وری شما را تا ۳۰۰ درصد افزایش دهد.",
        "category": "توسعه فردی",
        "tags": ["بهره‌وری", "موفقیت", "سبک زندگی"],
    }
]

class Command(BaseCommand):
    """
    Executes deep database alterations establishing base scenarios logically configured perfectly.
    """
    help: str = "Clears the blog database and seeds fake posts mapping them to existing local images."
    API_URL: str = "https://jsonplaceholder.typicode.com/posts"

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Coordinates complex internal setups applying initial values smoothly maintaining stability.
        """
        self.stdout.write("Starting blog database cleanup...")
        self._clear_database()
        
        self.stdout.write("Fetching external blog data...")
        data: List[Dict[str, Any]] = self._fetch_api_data(self.API_URL)
        
        if not data:
            self.stdout.write(self.style.WARNING("API failed. Using tailored Persian fallback data."))
            data = FALLBACK_DATA
        else:
            data = data[:10]
            self.stdout.write(self.style.WARNING("Using generic API data."))

        self.stdout.write("Seeding blog models...")
        self._seed_blog_data(data)
        
        self.stdout.write(self.style.SUCCESS("Blog database seeded successfully with LOCAL images!"))

    def _clear_database(self) -> None:
        """
        Erases complete relation cascades safely enforcing blank slate architectures completely.
        """
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()

    def _fetch_api_data(self, url: str) -> List[Dict[str, Any]]:
        """
        Dispatches remote requests resolving configurations precisely avoiding certificate boundaries naturally.
        """
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            return []

    def _get_random_local_image(self) -> Optional[str]:
        """
        Injects local logic randomly targeting distinct entities generating explicit file mappings safely.
        """
        try:
            blog_img_dir: str = os.path.join(settings.MEDIA_ROOT, 'blog', 'posts')
            if os.path.exists(blog_img_dir):
                images: List[str] = [f for f in os.listdir(blog_img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                if images:
                    return f"blog/posts/{random.choice(images)}"
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error accessing local media: {e}"))
        return None

    def _get_or_create_user(self) -> Any:
        """
        Determines user structure providing correct access configurations reliably identifying active authors.
        """
        user, _ = User.objects.get_or_create(
            username="blog_author",
            defaults={
                "email": "author@arkkala.com",
                "first_name": "مدیر",
                "last_name": "محتوا",
                "is_staff": True
            }
        )
        if not user.password:
            user.set_password("author123456")
            user.save()
        return user

    def _get_or_create_category(self, title: str) -> Category:
        """
        Processes generic data parsing components accurately defining models implicitly safely.
        """
        category, _ = Category.objects.get_or_create(
            title=title,
            defaults={'slug': slugify(title, allow_unicode=True)}
        )
        return category

    def _get_or_create_tag(self, title: str) -> Tag:
        """
        Resolves tag parameters systematically bridging internal metadata logically securely.
        """
        tag, _ = Tag.objects.get_or_create(
            title=title,
            defaults={'slug': slugify(title, allow_unicode=True)}
        )
        return tag

    def _seed_blog_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Translates raw input converting fields directly generating structured domain representations effortlessly.
        """
        author = self._get_or_create_user()
        
        for index, item in enumerate(data):
            cat_title: str = item.get("category", "اخبار عمومی")
            category: Category = self._get_or_create_category(cat_title)
            
            raw_title: str = item.get("title", f"مقاله شماره {index}")
            body: str = item.get("body", "محتوای پیش فرض مقاله.")
            
            post: Post = Post.objects.create(
                author=author,
                category=category,
                title=raw_title[:250],
                short_description=body[:150],
                body=body,
                view_count=10 * (index + 1),
                read_time=5,
                is_published=True,
                expert_reviewer="دکتر مهندسی نرم‌افزار",
                key_takeaways=[
                    "نکته کلیدی و مهم اول در این محتوا",
                    "نکته کلیدی دوم برای موتورهای هوش مصنوعی"
                ],
                citations=[
                    "https://scholar.google.com",
                    "https://nature.com"
                ],
                faq_data=[
                    {
                        "question": f"مهم‌ترین کاربرد {cat_title} چیست؟",
                        "answer": "این موضوع بستگی به نیاز کاربر و زیرساخت‌های سیستم دارد."
                    },
                    {
                        "question": "آیا این مقاله برای افراد مبتدی مناسب است؟",
                        "answer": "بله، تمام مفاهیم به ساده‌ترین شکل توضیح داده شده‌اند."
                    }
                ]
            )

            tags_data: List[str] = item.get("tags", ["عمومی", "مقاله"])
            for tag_title in tags_data:
                tag: Tag = self._get_or_create_tag(tag_title)
                post.tags.add(tag)

            local_image: Optional[str] = self._get_random_local_image()
            if local_image:
                post.image.name = local_image
                post.image_alt = post.title
                post.save(update_fields=['image', 'image_alt'])
                image_status: str = "Local Image Assigned"
            else:
                image_status = "No Local Image Found"

            Comment.objects.create(
                post=post,
                user=None,
                body=f"مقاله بسیار مفیدی بود، ممنون از اطلاعات خوبی که در مورد {cat_title} دادید.",
                is_approved=True
            )
            
            if index % 2 == 0:
                Comment.objects.create(
                    post=post,
                    user=author,
                    body="خواهش می‌کنم، در صورت داشتن سوال می‌توانید در همین بخش مطرح کنید.",
                    is_approved=True
                )

            self.stdout.write(f"Blog Post Created [{image_status}]: {post.title}")