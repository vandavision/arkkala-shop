import logging
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict, List
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from shop.models.category import Category
from shop.models.brand import Brand
from shop.models.product import Product, ProductGallery

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help: str = "Clears DB, fetches products from an external API, and seeds them with images."
    API_URL: str = "https://dummyjson.com/products?limit=40"
    SITE_NAME: str = "ارک کالا"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.session = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=1,
            status_forcelist=[403, 429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write(self.style.WARNING("Clearing database..."))
        self._clear_database()

        self.stdout.write(self.style.WARNING("Fetching data from external API..."))

        try:
            response = self.session.get(self.API_URL, timeout=20, verify=False)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            products: List[Dict[str, Any]] = data.get('products', [])

            if not products:
                self.stdout.write(self.style.ERROR("No products found in the API response."))
                return

            self.stdout.write(self.style.SUCCESS(f"Fetched {len(products)} products. Starting seed process..."))
            self._process_products(products)
            self.stdout.write(self.style.SUCCESS("Seeding completed successfully."))

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch data from API: {e}"))

    def _clear_database(self) -> None:
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

    def _process_products(self, products: List[Dict[str, Any]]) -> None:
        for item in products:
            try:
                self._create_product_transactional(item)
                self.stdout.write(self.style.SUCCESS(f"Seeded: {item.get('title')}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to seed {item.get('title')}: {e}"))

    @transaction.atomic
    def _create_product_transactional(self, item: Dict[str, Any]) -> None:
        category_title: str = item.get("category", "General").replace("-", " ").title()
        brand_title: str = item.get("brand", "Generic").title()

        category = self._get_or_create_category(category_title)
        brand = self._get_or_create_brand(brand_title)

        raw_title: str = item.get("title", "")[:250]
        desc: str = item.get("description", "")
        base_slug: str = slugify(raw_title, allow_unicode=True) or f"product-{item.get('id')}"

        if Product.objects.filter(slug=base_slug).exists():
            base_slug = f"{base_slug}-{item.get('id')}"

        price_usd: float = float(item.get("price", 10.0))
        price_irt: int = int(price_usd * 50000)
        
        reviews: List[Any] = item.get("reviews", [])
        calculated_views: int = len(reviews) * 25

        tags: List[str] = item.get("tags", [])
        
        product = Product.objects.create(
            category=category,
            brand=brand,
            title=raw_title,
            english_title=raw_title,
            slug=base_slug,
            short_description=(desc[:147] + "...") if len(desc) > 150 else desc,
            description=desc,
            base_price=price_irt,
            base_inventory=int(item.get("stock", 50)),
            weight=int(item.get("weight", 500)),
            volume=1000,
            is_active=True,
            average_rating=float(item.get("rating", 4.0)),
            view_count=calculated_views,
            sold_count=int(item.get("minimumOrderQuantity", 5)),
            keywords=[raw_title, category.title, brand.title, "خرید", self.SITE_NAME] + tags,
            meta_description=f"خرید {raw_title} با بهترین قیمت و ضمانت اصالت کالا در {self.SITE_NAME}.",
            og_title=f"{raw_title} | {self.SITE_NAME}",
            og_type="product",
            og_description=desc[:200],
            og_site_name=self.SITE_NAME,
            og_locale="en_US",
            twitter_card="summary_large_image",
            twitter_site="@arkkala",
            twitter_creator="@arkkala",
            expert_reviewer="تیم بررسی هوشمند سیستم",
            key_takeaways=tags,
            citations=[f"اطلاعات رسمی سازنده {brand.title}", "تست و بررسی فنی مجموعه"]
        )

        images: List[str] = item.get("images", [])
        if not images:
            raise ValueError("API returned no images for this product.")

        for idx, image_url in enumerate(images):
            self._download_and_attach_image(product, image_url, is_main=(idx == 0))

    def _get_or_create_category(self, title: str) -> Category:
        slug_val: str = slugify(title, allow_unicode=True)
        category, _ = Category.objects.get_or_create(
            title=title,
            defaults={
                'slug': slug_val,
                'keywords': [title, "دسته بندی", self.SITE_NAME],
                'meta_description': f"محصولات دسته {title}",
                'og_title': title,
                'og_type': "website",
                'og_site_name': self.SITE_NAME,
            }
        )
        return category

    def _get_or_create_brand(self, title: str) -> Brand:
        slug_val: str = slugify(title, allow_unicode=True)
        brand, _ = Brand.objects.get_or_create(
            title=title,
            defaults={
                'slug': slug_val,
                'keywords': [title, "برند", self.SITE_NAME],
                'meta_description': f"محصولات برند {title}",
                'og_title': title,
                'og_type': "website",
                'og_site_name': self.SITE_NAME,
            }
        )
        return brand

    def _download_and_attach_image(self, product: Product, url: str, is_main: bool) -> None:
        try:
            response = self.session.get(url, timeout=20, verify=False)
            response.raise_for_status()
            
            file_extension: str = url.split("?")[0].split(".")[-1][:4]
            if file_extension.lower() not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                file_extension = 'jpg'

            filename: str = f"product_{product.uuid}_{'main' if is_main else 'sub'}.{file_extension}"
            image_content = ContentFile(response.content, name=filename)
            
            ProductGallery.objects.create(
                product=product,
                image=image_content,
                image_alt=product.title,
                is_main=is_main
            )
        except Exception as e:
            logger.warning(f"Failed to download image from {url} for product {product.uuid}: {e}")
            raise e