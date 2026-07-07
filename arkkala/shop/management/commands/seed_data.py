import random
from typing import Any, Dict
from datetime import timedelta

import requests
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from faker import Faker

from shop.models import (
    Category as ShopCategory, Brand, Product, Attribute, AttributeValue, 
    ProductVariant, ProductGallery, ProductVideo, Comment as ShopComment,
    Question, PriceHistory
)
from blog.models import Category as BlogCategory, Tag, Post
from home.models import Story, Slider, Banner, StoreReview
from orders.models import ShippingMethod, Coupon

User = get_user_model()


class Command(BaseCommand):
    """
    Command to populate the database with comprehensive, realistic test data for the Arkkala project.
    Seeds the database with fake data, real placeholder images, and videos.
    """
    help = 'Seeds the database with fake data, real placeholder images, and videos.'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the command and set up caches for images and videos.
        """
        super().__init__(*args, **kwargs)
        self.image_cache: Dict[str, bytes] = {}
        self.video_cache: bytes | None = None

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Add custom arguments to the command.
        """
        parser.add_argument('--records', type=int, default=15, help='Number of primary records to generate')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def _get_realistic_image(self, category: str, width: int, height: int, index: int) -> ContentFile:
        """
        Fetches a real image from picsum.photos. Uses a cache to avoid slow seeding.
        """
        cache_key = f"{category}_{index % 5}"

        if cache_key not in self.image_cache:
            self.stdout.write(f"Downloading image for {cache_key} ({width}x{height})...")
            url = f"https://picsum.photos/seed/{cache_key}/{width}/{height}"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                self.image_cache[cache_key] = response.content
            except requests.RequestException:
                self.stdout.write(self.style.WARNING(f"Failed to fetch {url}. Using empty image."))
                return ContentFile(b"", name=f"empty_{cache_key}.jpg")

        return ContentFile(self.image_cache[cache_key], name=f"{cache_key}.jpg")

    def _get_realistic_video(self) -> ContentFile:
        """
        Fetches a real sample video. Uses cache to download only once.
        """
        if self.video_cache is None:
            self.stdout.write("Downloading sample video for products...")
            url = "https://www.w3schools.com/html/mov_bbb.mp4"
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                self.video_cache = response.content
            except requests.RequestException:
                self.stdout.write(self.style.WARNING(f"Failed to fetch video from {url}. Using empty video."))
                self.video_cache = b""

        return ContentFile(self.video_cache, name="sample_video.mp4")

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Main execution logic for seeding the database.
        """
        fake = Faker(['fa_IR'])
        records_count: int = options['records']

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing all old data...'))
            User.objects.exclude(is_superuser=True).delete()
            ShopCategory.objects.all().delete()
            Brand.objects.all().delete()
            Product.objects.all().delete()
            Attribute.objects.all().delete()
            BlogCategory.objects.all().delete()
            Tag.objects.all().delete()
            Post.objects.all().delete()
            Story.objects.all().delete()
            Slider.objects.all().delete()
            Banner.objects.all().delete()
            StoreReview.objects.all().delete()
            ShippingMethod.objects.all().delete()
            Coupon.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All data cleared.'))

        self.stdout.write('Seeding Users...')
        users = []
        for _ in range(5):
            user = User.objects.create_user(
                email=fake.unique.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=fake.msisdn()
            )
            users.append(user)

        self.stdout.write('Seeding Home Page CMS (Stories, Sliders, Banners)...')
        for i in range(6):
            story = Story(title=fake.word() + f" {i}", is_active=True)
            story.image.save(f"story_{i}.jpg", self._get_realistic_image('story', 400, 400, i), save=True)

        for i in range(3):
            slider = Slider(title=fake.sentence(nb_words=3) + f" {i}", order=i, is_active=True)
            slider.image.save(f"slider_{i}.jpg", self._get_realistic_image('slider', 1600, 500, i), save=True)

        banners_data = [("بنر تخفیف بهاره", "top_left"), ("جشنواره لپ‌تاپ", "middle_row")]
        for i, (title, pos) in enumerate(banners_data):
            banner = Banner(title=f"{title} {i}", position=pos)
            banner.image.save(f"banner_{i}.jpg", self._get_realistic_image('banner', 800, 400, i), save=True)

        for _ in range(4):
            StoreReview.objects.create(user_name=fake.name(), body=fake.paragraph(nb_sentences=2))

        self.stdout.write('Seeding Shop Categories & Brands...')
        shop_cats = []
        for i in range(5):
            cat = ShopCategory.objects.create(
                title=fake.word() + f" دسته {i}", 
                slug=slugify(fake.word() + str(i), allow_unicode=True)
            )
            cat.image.save(f"category_{i}.jpg", self._get_realistic_image('category', 200, 200, i), save=True)
            shop_cats.append(cat)

        brands = []
        for i in range(8):
            brand = Brand(title=fake.company() + f" برند {i}", slug=slugify(fake.company() + str(i), allow_unicode=True))
            brand.logo.save(f"brand_{i}.jpg", self._get_realistic_image('logo', 200, 200, i), save=True)
            brands.append(brand)

        color_attr, _ = Attribute.objects.get_or_create(title="رنگ", defaults={"slug": "color"})
        size_attr, _ = Attribute.objects.get_or_create(title="حافظه / سایز", defaults={"slug": "size"})

        attr_vals = [
            AttributeValue.objects.get_or_create(attribute=color_attr, value="مشکی")[0],
            AttributeValue.objects.get_or_create(attribute=color_attr, value="سفید")[0],
            AttributeValue.objects.get_or_create(attribute=size_attr, value="256GB")[0],
            AttributeValue.objects.get_or_create(attribute=size_attr, value="512GB")[0]
        ]

        self.stdout.write('Seeding Products, Galleries, Videos, Variants, Comments & Questions...')
        for i in range(records_count):
            is_variable = random.choice([True, False])
            base_price = random.randint(50000, 5000000) * 10
            title = fake.sentence(nb_words=3) + f" مدل {i}"
            
            # Setting up special offer logic
            is_special = random.choice([True, False])
            special_percent = random.randint(5, 40) if is_special else 0
            special_end = timezone.now() + timedelta(days=random.randint(1, 10)) if is_special else None

            product = Product.objects.create(
                title=title,
                slug=slugify(title, allow_unicode=True),
                english_title=fake.word() + f" model {i}",
                category=random.choice(shop_cats),
                brand=random.choice(brands),
                short_description=fake.text(max_nb_chars=120),
                description=fake.paragraph(nb_sentences=6),
                base_price=base_price,
                base_inventory=random.randint(0, 50) if not is_variable else 0,
                weight=random.randint(100, 5000),
                volume=random.randint(500, 5000),
                is_wholesale=random.choice([True, False]),
                wholesale_min_quantity=random.randint(5, 15),
                wholesale_base_price=base_price * 0.8,
                special_discount_percent=special_percent,
                special_offer_end=special_end,
                is_variable=is_variable,
                view_count=random.randint(10, 5000),
                sold_count=random.randint(0, 100)
            )

            # Generate Price History (Chart data)
            for days_ago in range(6, 0, -1):
                past_date = timezone.now() - timedelta(days=days_ago)
                history = PriceHistory.objects.create(
                    product=product,
                    price=base_price * random.uniform(0.8, 1.2)
                )
                PriceHistory.objects.filter(pk=history.pk).update(created_at=past_date)

            gallery = ProductGallery(product=product, is_main=True)
            gallery.image.save(f"product_{i}.jpg", self._get_realistic_image('product', 600, 600, i), save=True)

            if random.choice([True, False]):
                video = ProductVideo(product=product, title=f"ویدیوی معرفی {title}")
                video.video_file.save(f"video_{i}.mp4", self._get_realistic_video(), save=True)

            if is_variable:
                for _ in range(2):
                    var = ProductVariant.objects.create(
                        product=product,
                        price=base_price + random.randint(10000, 500000),
                        inventory=random.randint(5, 20),
                        wholesale_price=base_price * 0.75
                    )
                    var.attribute_values.add(random.choice(attr_vals))

            # Generate Comments
            for _ in range(random.randint(0, 3)):
                ShopComment.objects.create(
                    product=product, user=random.choice(users), body=fake.paragraph(nb_sentences=2),
                    rating=random.randint(3, 5), is_approved=True
                )
                
            # Generate Questions
            for _ in range(random.randint(0, 2)):
                has_answer = random.choice([True, False])
                Question.objects.create(
                    product=product,
                    user=random.choice([random.choice(users), None]),
                    name=fake.name() if random.choice([True, False]) else None,
                    text=fake.sentence(nb_words=10) + "؟",
                    answer_text=fake.paragraph(nb_sentences=2) if has_answer else None,
                    is_approved=True
                )

        self.stdout.write('Seeding Blog Posts...')
        blog_cats = [BlogCategory.objects.create(title=fake.word() + f" دسته بلاگ {i}", slug=slugify(fake.word() + str(i), allow_unicode=True)) for i in range(4)]
        tags = [Tag.objects.create(title=fake.word() + f" برچسب {i}", slug=slugify(fake.word() + str(i), allow_unicode=True)) for i in range(6)]

        for i in range(records_count // 2):
            post_title = fake.sentence(nb_words=4) + f" {i}"
            post = Post(
                title=post_title,
                slug=slugify(post_title, allow_unicode=True),
                author=random.choice(users),
                category=random.choice(blog_cats),
                short_description=fake.text(max_nb_chars=100),
                body=fake.paragraph(nb_sentences=15),
                view_count=random.randint(50, 2000),
                read_time=random.randint(3, 12)
            )
            post.image.save(f"post_{i}.jpg", self._get_realistic_image('blog', 800, 600, i), save=False)
            post.save()
            post.tags.add(*random.sample(tags, 2))

        self.stdout.write('Seeding Shipping Methods & Coupons...')
        ShippingMethod.objects.get_or_create(name="پست پیشتاز", defaults={"base_cost": 45000, "is_pay_on_delivery": False})
        ShippingMethod.objects.get_or_create(name="تیپاکس (پس کرایه)", defaults={"base_cost": 0, "is_pay_on_delivery": True})

        Coupon.objects.get_or_create(
            code="SPRING1403",
            defaults={
                "discount_percent": 15,
                "max_discount_amount": 100000,
                "valid_from": timezone.now(),
                "valid_to": timezone.now() + timedelta(days=30),
                "usage_limit": 100
            }
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {records_count} complete records with REAL images and videos! 🚀'))