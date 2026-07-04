import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from shop.models import Category as ShopCategory, Brand, Product, Attribute, AttributeValue, ProductVariant
from blog.models import Category as BlogCategory, Tag, Post

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with fake data for testing purposes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--records',
            type=int,
            default=15,
            help='Number of records to generate per model (default: 15)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        fake = Faker(['fa_IR'])
        records_count = options['records']

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing old data...'))
            User.objects.exclude(is_superuser=True).delete()
            ShopCategory.objects.all().delete()
            Brand.objects.all().delete()
            Product.objects.all().delete()
            Attribute.objects.all().delete()
            BlogCategory.objects.all().delete()
            Tag.objects.all().delete()
            Post.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared.'))

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

        self.stdout.write('Seeding Shop Categories...')
        shop_categories = []
        for i in range(5):
            title = fake.word() + f" فروشگاهی {i}"
            cat = ShopCategory.objects.create(
                title=title,
                slug=slugify(title, allow_unicode=True)
            )
            shop_categories.append(cat)

        self.stdout.write('Seeding Brands...')
        brands = []
        for i in range(5):
            title = fake.company() + f" برند {i}"
            brand = Brand.objects.create(
                title=title,
                slug=slugify(title, allow_unicode=True)
            )
            brands.append(brand)

        self.stdout.write('Seeding Attributes...')
        color_attr = Attribute.objects.create(title="رنگ", slug="color")
        size_attr = Attribute.objects.create(title="سایز", slug="size")
        
        red = AttributeValue.objects.create(attribute=color_attr, value="قرمز")
        blue = AttributeValue.objects.create(attribute=color_attr, value="آبی")
        small = AttributeValue.objects.create(attribute=size_attr, value="کوچک")
        large = AttributeValue.objects.create(attribute=size_attr, value="بزرگ")

        self.stdout.write('Seeding Products...')
        for i in range(records_count):
            title = fake.sentence(nb_words=3) + f" {i}"
            is_variable = random.choice([True, False])
            base_price = random.randint(100000, 5000000)
            
            product = Product.objects.create(
                title=title,
                slug=slugify(title, allow_unicode=True),
                english_title=fake.word(),
                category=random.choice(shop_categories),
                brand=random.choice(brands),
                short_description=fake.text(max_nb_chars=150),
                description=fake.paragraph(nb_sentences=5),
                base_price=base_price,
                base_inventory=random.randint(0, 50) if not is_variable else 0,
                is_wholesale=random.choice([True, False]),
                wholesale_min_quantity=random.randint(5, 20),
                wholesale_base_price=base_price * 0.8,
                is_variable=is_variable
            )

            if is_variable:
                variant1 = ProductVariant.objects.create(
                    product=product,
                    price=base_price + 50000,
                    inventory=random.randint(5, 20),
                    wholesale_price=base_price * 0.75
                )
                variant1.attribute_values.add(red, small)

                variant2 = ProductVariant.objects.create(
                    product=product,
                    price=base_price + 80000,
                    inventory=random.randint(5, 20),
                    wholesale_price=base_price * 0.75
                )
                variant2.attribute_values.add(blue, large)

        self.stdout.write('Seeding Blog Data...')
        blog_categories = []
        for i in range(3):
            title = fake.word() + f" بلاگ {i}"
            bcat = BlogCategory.objects.create(
                title=title,
                slug=slugify(title, allow_unicode=True)
            )
            blog_categories.append(bcat)

        tags = []
        for i in range(5):
            title = fake.word() + f" تگ {i}"
            tag = Tag.objects.create(
                title=title,
                slug=slugify(title, allow_unicode=True)
            )
            tags.append(tag)

        for i in range(records_count // 2):
            title = fake.sentence(nb_words=4) + f" پست {i}"
            post = Post.objects.create(
                title=title,
                slug=slugify(title, allow_unicode=True),
                author=random.choice(users),
                category=random.choice(blog_categories),
                short_description=fake.text(max_nb_chars=100),
                body=fake.paragraph(nb_sentences=10),
                view_count=random.randint(10, 1000)
            )
            post.tags.add(*random.sample(tags, 2))

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {records_count} records per model! 🎉'))