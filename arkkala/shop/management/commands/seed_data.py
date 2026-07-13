"""
Master Database Seeder for Arkkala E-Commerce.
Generates Massive and Extremely Rich Fake Data for Users, Blog, Shop, Orders, and Payments.
Includes complete SEO, AEO, and GEO implementations with Multiple Gallery Images.
"""
import random
from decimal import Decimal
from typing import List, Dict, Any

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from faker import Faker

# Import Models
from blog.models import Category as BlogCategory, Tag, Post, Comment as BlogComment
from shop.models import (
    Category as ShopCategory, Brand, Attribute, AttributeValue,
    Product, ProductGallery, ProductVariant, Comment as ShopComment, Question
)
from orders.models import ShippingMethod, Coupon, Cart, CartItem, Order, OrderItem
from payments.models import Transaction

User = get_user_model()
fake = Faker('fa_IR')

# لیستی از تصاویر واقعی موجود در ساختار فایل‌های شما برای جلوگیری از 404
PRODUCT_IMAGES = [f'products/gallery/product_{i}.jpg' for i in range(20)]
BLOG_IMAGES = [f'blog/posts/post_{i}.jpg' for i in range(10)]
BRAND_LOGOS = [f'brands/logos/brand_{i}.jpg' for i in range(8)]
CATEGORY_IMAGES = [f'categories/images/category_{i}.jpg' for i in range(5)]


class Command(BaseCommand):
    help = 'ایجاد داده‌های تستی حجیم و ساختاریافته (Fake Data) همراه با سئو، AEO و GEO کامل'

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(self.style.WARNING('شروع فرآیند تولید داده‌های حجیم... لطفاً صبور باشید.'))

        with transaction.atomic():
            self._create_users()
            self._create_blog_data()
            self._create_shop_data()
            self._create_orders_and_payments()

        self.stdout.write(self.style.SUCCESS('✅ دیتابیس با موفقیت با داده‌های بسیار غنی (گالری، سئو، هوش مصنوعی) پر شد!'))

    def _create_users(self) -> None:
        self.stdout.write('در حال ایجاد کاربران (با حل مشکل Username)...')
        
        # Admin
        if not User.objects.filter(email='admin@arkkala.com').exists():
            try:
                # Passing both username and email to cover different CustomUser implementations
                User.objects.create_superuser('admin_user', 'admin@arkkala.com', 'admin123', first_name='مدیر', last_name='سایت')
            except TypeError:
                User.objects.create_superuser(username='admin_user', email='admin@arkkala.com', password='admin123', first_name='مدیر', last_name='سایت')

        # Normal Users (Create 15 users for variety)
        self.users = []
        for i in range(1, 16):
            username = f'user_{i}_{fake.user_name()}'
            email = f'user{i}@test.com'
            phone = f"0912{random.randint(1000000, 9999999)}"
            
            if not User.objects.filter(email=email).exists():
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='password123',
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        phone_number=phone
                    )
                except TypeError:
                    user = User.objects.create_user(
                        username=username,
                        password='password123',
                        email=email,
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        phone_number=phone
                    )
                self.users.append(user)
            else:
                self.users.append(User.objects.get(email=email))

    def _create_blog_data(self) -> None:
        self.stdout.write('در حال ایجاد داده‌های مجله (SEO, AEO, GEO مقالات)...')
        
        # Blog Categories
        b_cats = []
        for title in ['بررسی گجت‌ها', 'اخبار تکنولوژی', 'راهنمای خرید', 'هوش مصنوعی', 'آموزش و ترفند']:
            cat, _ = BlogCategory.objects.get_or_create(
                title=title, 
                defaults={
                    'meta_description': f'جدیدترین مقالات در زمینه {title} را در ارک کالا بخوانید.',
                    'keywords': f"{title}, مقاله {title}, آموزش {title}"
                }
            )
            b_cats.append(cat)

        # Tags
        tags = []
        for title in ['اپل', 'اندروید', 'لپ‌تاپ', 'گیمینگ', 'برنامه‌نویسی', 'گوشی موبایل', 'سخت‌افزار']:
            tag, _ = Tag.objects.get_or_create(title=title)
            tags.append(tag)

        # Posts (25 Rich Posts)
        for i in range(25):
            post_title = f"بررسی تخصصی {fake.word()}؛ {fake.sentence(nb_words=5)}"
            post, created = Post.objects.get_or_create(
                title=post_title,
                defaults={
                    'author': random.choice(self.users) if self.users else None,
                    'category': random.choice(b_cats),
                    'image': random.choice(BLOG_IMAGES),
                    'image_alt': f"تصویر شاخص مقاله {post_title}", # SEO
                    'short_description': fake.paragraph(nb_sentences=3),
                    'body': f"<h3>مقدمه</h3><p>{fake.paragraph(nb_sentences=8)}</p><h3>طراحی و ساخت</h3><p>{fake.paragraph(nb_sentences=10)}</p><h3>عملکرد و کارایی</h3><p>{fake.paragraph(nb_sentences=12)}</p><h3>نتیجه‌گیری</h3><p>{fake.paragraph(nb_sentences=4)}</p>",
                    
                    # GEO Signals
                    'expert_reviewer': f"دکتر {fake.last_name()} - متخصص سخت‌افزار",
                    'key_takeaways': [
                        "طراحی ارگونومیک و استفاده از متریال با کیفیت در بدنه.",
                        "عمر باتری بهبود یافته نسبت به نسل‌های گذشته.",
                        "پشتیبانی از فناوری‌های جدید ارتباطی و پردازش سریع‌تر.",
                        "ارزش خرید بالا با توجه به قیمت رقابتی در بازار."
                    ],
                    'citations': [
                        "https://www.theverge.com/tech-reviews",
                        "https://www.gsmarena.com/reviews",
                        "https://arxiv.org/abs/sample-tech-paper"
                    ],
                    
                    # AEO Signal
                    'faq_data': [
                        {"question": f"مهم‌ترین مزیت {fake.word()} چیست؟", "answer": fake.paragraph(nb_sentences=2)},
                        {"question": "آیا این مدل از فست شارژ پشتیبانی می‌کند؟", "answer": "بله، طبق بررسی‌های انجام شده دارای سیستم شارژ سریع فوق‌العاده‌ای است."},
                        {"question": "ارزش خرید این محصول نسبت به رقبا چگونه است؟", "answer": fake.paragraph(nb_sentences=2)}
                    ],
                    
                    # SEO Meta
                    'meta_description': f"در این مقاله به بررسی دقیق و تخصصی {post_title} می‌پردازیم. نظرات کارشناسان و تست‌های عملکرد...",
                    'keywords': f"{fake.word()}, بررسی تخصصی, ارک کالا, تکنولوژی",
                    
                    'view_count': random.randint(500, 15000),
                    'read_time': random.randint(4, 25),
                }
            )
            if created:
                post.tags.set(random.sample(tags, k=random.randint(2, 4)))
                # Comments (5 to 10 comments per post)
                for _ in range(random.randint(5, 10)):
                    BlogComment.objects.create(
                        post=post,
                        user=random.choice(self.users),
                        body=fake.paragraph(nb_sentences=2),
                        is_approved=True
                    )

    def _create_shop_data(self) -> None:
        self.stdout.write('در حال ایجاد داده‌های فروشگاه (گالری چندتایی، AEO، GEO محصولات)...')

        # Brands
        self.brands = []
        brand_names = ['اپل', 'سامسونگ', 'شیائومی', 'سونی', 'ال‌جی', 'ایسوس', 'لنوو', 'هوآوی']
        for i, title in enumerate(brand_names):
            logo_path = BRAND_LOGOS[i] if i < len(BRAND_LOGOS) else BRAND_LOGOS[0]
            brand, _ = Brand.objects.get_or_create(
                title=title, 
                defaults={
                    'logo': logo_path,
                    'logo_alt': f"لوگوی برند {title}", # SEO
                    'meta_description': f"خرید تمامی محصولات اصلی برند {title} با گارانتی معتبر در ارک کالا."
                }
            )
            self.brands.append(brand)

        # Categories
        self.s_cats = []
        parent_cat, _ = ShopCategory.objects.get_or_create(
            title='کالای دیجیتال',
            defaults={'image': CATEGORY_IMAGES[0], 'image_alt': 'کالای دیجیتال ارک کالا'}
        )
        cat_names = ['گوشی موبایل', 'لپ‌تاپ', 'ساعت هوشمند', 'تبلت', 'لوازم جانبی']
        for i, title in enumerate(cat_names):
            img_path = CATEGORY_IMAGES[i % len(CATEGORY_IMAGES)]
            cat, _ = ShopCategory.objects.get_or_create(
                title=title, 
                parent=parent_cat,
                defaults={'image': img_path, 'image_alt': f'دسته بندی {title}'}
            )
            self.s_cats.append(cat)

        # Attributes for Variants
        color_attr, _ = Attribute.objects.get_or_create(title='رنگ')
        size_attr, _ = Attribute.objects.get_or_create(title='ظرفیت حافظه')
        
        colors = ['مشکی', 'سفید', 'آبی', 'قرمز', 'نقره‌ای']
        sizes = ['64GB', '128GB', '256GB', '512GB', '1TB']
        
        self.colors = [AttributeValue.objects.get_or_create(attribute=color_attr, value=v)[0] for v in colors]
        self.sizes = [AttributeValue.objects.get_or_create(attribute=size_attr, value=v)[0] for v in sizes]

        # 40 Rich Products
        self.products = []
        for i in range(40):
            is_variable = random.choice([True, True, False]) # 66% chance of being variable
            base_price = Decimal(random.randint(50, 1000) * 100000) # 5M to 100M
            prod_brand = random.choice(self.brands)
            prod_cat = random.choice(self.s_cats)
            product_title = f"{prod_cat.title} {prod_brand.title} مدل {fake.word().upper()}-{random.randint(100, 900)}"
            
            product, created = Product.objects.get_or_create(
                title=product_title,
                defaults={
                    'english_title': f"{prod_brand.title} {prod_cat.title} {random.randint(100, 900)} Series",
                    'category': prod_cat,
                    'brand': prod_brand,
                    'short_description': f"محصولی شگفت‌انگیز از {prod_brand.title} با طراحی منحصربه‌فرد و عملکرد استثنایی. {fake.paragraph(nb_sentences=2)}",
                    'description': f"<h3>معرفی جامع</h3><p>{fake.paragraph(nb_sentences=7)}</p><h3>طراحی</h3><p>{fake.paragraph(nb_sentences=5)}</p>",
                    
                    # GEO Signals
                    'expert_reviewer': f"مهندس {fake.last_name()} - تست شده در لابراتوار ارک کالا",
                    'key_takeaways': [
                        "پردازنده فوق سریع هشت هسته‌ای با معماری جدید",
                        "نمایشگر با کیفیت بالا و نرخ نوسازی 120 هرتز",
                        "بدنه مقاوم در برابر آب و گرد و غبار (گواهی IP68)",
                        "پشتیبانی از شارژ بی‌سیم و شارژ معکوس",
                        f"گارانتی ۱۸ ماهه رسمی {prod_brand.title}"
                    ],
                    'citations': [f"https://www.{prod_brand.slug}.com/official-specs", "https://techradar.com/review"],
                    
                    # SEO Meta
                    'meta_description': f"خرید اینترنتی {product_title} با بهترین قیمت و ضمانت اصالت. مشخصات کامل و نقد و بررسی...",
                    'keywords': f"خرید {product_title}, قیمت {prod_cat.title} {prod_brand.title}",
                    
                    'base_price': base_price,
                    'base_inventory': 0 if is_variable else random.randint(10, 100),
                    'weight': random.randint(150, 2500),
                    'is_variable': is_variable,
                    'sold_count': random.randint(10, 500),
                    'view_count': random.randint(500, 25000),
                    'average_rating': round(random.uniform(4.0, 5.0), 1),
                    
                    # Offers & Wholesale
                    'special_discount_percent': random.choice([0, 0, 15, 30]) if not is_variable else 0,
                    'special_offer_end': timezone.now() + timezone.timedelta(days=random.randint(1, 5)) if not is_variable else None,
                    'is_wholesale': random.choice([True, False]),
                    'wholesale_min_quantity': random.randint(5, 10),
                    'wholesale_base_price': base_price * Decimal('0.85'), # 15% cheaper for wholesale
                }
            )
            
            if created:
                self.products.append(product)
                
                # --- Multiple Gallery Images (SEO `image_alt` integrated) ---
                num_images = random.randint(3, 5) # Create 3 to 5 images per product
                selected_images = random.sample(PRODUCT_IMAGES, num_images)
                
                for idx, img_path in enumerate(selected_images):
                    ProductGallery.objects.create(
                        product=product,
                        image=img_path,
                        image_alt=f"تصویر {idx + 1} از {product.title} با نمای دقیق", # SEO signal
                        is_main=(idx == 0) # First image is main
                    )

                # --- Variants ---
                if is_variable:
                    selected_colors = random.sample(self.colors, k=random.randint(2, 4))
                    for color in selected_colors:
                        # Randomize price based on color/size
                        var_price = base_price + Decimal(random.randint(0, 5) * 200000)
                        var = ProductVariant.objects.create(
                            product=product,
                            price=var_price,
                            inventory=random.randint(5, 40),
                            wholesale_price=var_price * Decimal('0.85') if product.is_wholesale else None
                        )
                        # Add a color and a random size
                        var.attribute_values.add(color, random.choice(self.sizes))

                # --- Shop Comments & Ratings ---
                for _ in range(random.randint(4, 12)):
                    ShopComment.objects.create(
                        product=product,
                        user=random.choice(self.users),
                        body=f"نقاط قوت: {fake.word()} و {fake.word()}\nنقاط ضعف: ندارد\n\nتوضیحات: {fake.paragraph(nb_sentences=2)}",
                        rating=random.randint(4, 5),
                        is_approved=True
                    )

                # --- AEO: Questions and Answers ---
                # AEO heavily relies on FAQ Schema which reads from these Q&A models.
                for _ in range(random.randint(3, 6)):
                    Question.objects.create(
                        product=product,
                        user=random.choice(self.users),
                        text=f"آیا {product_title} برای اجرای بازی‌های سنگین مناسب است یا داغ می‌کند؟",
                        answer_text=f"بله دوست عزیز. این مدل با توجه به سیستم خنک‌کننده پیشرفته و هیت‌سینک قوی، در پردازش‌های سنگین هم عملکرد پایداری دارد. {fake.sentence()}",
                        is_approved=True
                    )

    def _create_orders_and_payments(self) -> None:
        self.stdout.write('در حال ایجاد داده‌های سفارشات و پرداخت‌ها (تاریخچه خرید کاربران)...')

        # Shipping Methods
        post, _ = ShippingMethod.objects.get_or_create(
            name='پست پیشتاز', 
            defaults={'base_cost': 45000, 'is_pay_on_delivery': False, 'description': 'ارسال ایمن به سراسر کشور طی ۳ تا ۵ روز کاری'}
        )
        tipax, _ = ShippingMethod.objects.get_or_create(
            name='تیپاکس (پس کرایه)', 
            defaults={'base_cost': 0, 'is_pay_on_delivery': True, 'description': 'ارسال سریع، پرداخت هزینه پیک درب منزل'}
        )
        shipping_methods = [post, tipax]

        # Coupons
        Coupon.objects.get_or_create(
            code='FESTIVAL2026', 
            defaults={
                'discount_percent': 15, 
                'max_discount_amount': 200000,
                'valid_from': timezone.now() - timezone.timedelta(days=5),
                'valid_to': timezone.now() + timezone.timedelta(days=60),
                'usage_limit': 1000
            }
        )

        # Create massive realistic past orders
        statuses = ['delivered', 'delivered', 'delivered', 'shipped', 'processing', 'cancelled']
        
        for user in self.users:
            # Each user gets 2 to 6 past orders
            for i in range(random.randint(2, 6)):
                method = random.choice(shipping_methods)
                order_status = random.choice(statuses)
                
                order = Order.objects.create(
                    user=user,
                    status=order_status,
                    shipping_method=method,
                    title=random.choice(['خانه', 'محل کار', 'خوابگاه']),
                    country='ایران',
                    province=random.choice(['تهران', 'خوزستان', 'اصفهان', 'فارس']),
                    city=fake.city(),
                    postal_address=fake.address(),
                    postal_code=f"1234{random.randint(100000, 999999)}",
                    is_paid=(order_status != 'cancelled'),
                )

                # Add 1 to 4 distinct items to this order
                total_price = Decimal(0)
                selected_products = random.sample(self.products, k=random.randint(1, 4))
                
                for product in selected_products:
                    variant = product.variants.first() if product.is_variable else None
                    unit_price = variant.price if variant else product.base_price
                    qty = random.randint(1, 3)
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        variant=variant,
                        quantity=qty,
                        unit_price=unit_price,
                        total_price=unit_price * qty
                    )
                    total_price += (unit_price * qty)

                # Tax and Totals
                tax = total_price * Decimal('0.10')
                shipping_cost = Decimal('0') if method.is_pay_on_delivery else method.base_cost
                
                order.total_items_amount = total_price
                order.shipping_cost = shipping_cost
                order.payable_amount = total_price + tax + shipping_cost
                if order_status == 'delivered' or order_status == 'shipped':
                    order.tracking_code = f"IRPOST-{random.randint(100000000, 999999999)}"
                order.save()

                # Create Transaction if paid
                if order.is_paid:
                    Transaction.objects.create(
                        user=user,
                        order=order,
                        amount=order.payable_amount,
                        status='successful',
                        gateway=random.choice(['zarinpal', 'saman']),
                        authority=f"A00000000000000000000000000{random.randint(100000, 999999)}",
                        ref_id=f"{random.randint(1000000, 9999999)}"
                    )