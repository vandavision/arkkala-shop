import json
import ssl
import urllib.request
from typing import Any, Dict, List, Optional
from urllib.error import URLError

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop.models import (
    Attribute, AttributeValue, Brand, Category, Product, ProductGallery,
    ProductVideo, ProductVariant
)

FALLBACK_DATA: List[Dict[str, Any]] = [
    {
        "title": "iPhone 15 Pro Max",
        "price": 1200,
        "description": "The latest Apple flagship with titanium body and advanced camera.",
        "category": "Digital",
        "image": "https://picsum.photos/800/800?random=1",
        "rating": {"rate": 4.8, "count": 120}
    },
    {
        "title": "ASUS ROG Strix G16",
        "price": 1500,
        "description": "Powerful gaming laptop with Core i7 processor and RTX 4060 graphics.",
        "category": "Laptops",
        "image": "https://picsum.photos/800/800?random=2",
        "rating": {"rate": 4.5, "count": 85}
    },
    {
        "title": "Samsung Galaxy Watch 6",
        "price": 300,
        "description": "Smartwatch with health tracking and Super AMOLED display.",
        "category": "Smart Gadgets",
        "image": "https://picsum.photos/800/800?random=3",
        "rating": {"rate": 4.2, "count": 200}
    },
    {
        "title": "Sony WH-1000XM5 Wireless Headphones",
        "price": 400,
        "description": "Industry leading noise canceling headphones.",
        "category": "Accessories",
        "image": "https://picsum.photos/800/800?random=4",
        "rating": {"rate": 4.9, "count": 340}
    },
    {
        "title": "PlayStation 5 Console",
        "price": 500,
        "description": "Next generation gaming console with DualSense controller.",
        "category": "Gaming",
        "image": "https://picsum.photos/800/800?random=5",
        "rating": {"rate": 4.7, "count": 500}
    }
]

DUMMY_IMAGE_BYTES: bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'


class Command(BaseCommand):
    """Management command to seed the database robustly with fallbacks."""

    help: str = "Clears the database and seeds products using API or fallback data."
    API_URL: str = "https://fakestoreapi.com/products"
    VIDEO_URL: str = "https://www.w3schools.com/html/mov_bbb.mp4"

    def handle(self, *args: Any, **options: Any) -> None:
        """Main entry point for the command."""
        self.stdout.write("Starting database cleanup...")
        self.clear_database()
        
        self.stdout.write("Fetching product data...")
        data = self.fetch_api_data(self.API_URL)
        
        if not data:
            self.stdout.write(self.style.WARNING("API failed. Using fallback data."))
            data = FALLBACK_DATA

        self.stdout.write("Seeding products...")
        self.seed_products(data)
        
        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))

    def clear_database(self) -> None:
        """Deletes all existing shop data to prevent duplicates."""
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Attribute.objects.all().delete()

    def fetch_api_data(self, url: str) -> List[Dict[str, Any]]:
        """Fetches JSON data from the provided URL, ignoring SSL verification."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception:
            return []

    def download_file(self, url: str, filename: str, is_image: bool = True) -> Optional[ContentFile]:
        """Downloads a file from a URL, returns a dummy file on failure if it is an image."""
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
        """Retrieves or creates a Category by title."""
        category, _ = Category.objects.get_or_create(
            title=title,
            defaults={'slug': slugify(title, allow_unicode=True)}
        )
        return category

    def get_or_create_brand(self, title: str) -> Brand:
        """Retrieves or creates a Brand by title."""
        brand, _ = Brand.objects.get_or_create(
            title=title,
            defaults={'slug': slugify(title, allow_unicode=True)}
        )
        return brand

    def seed_products(self, data: List[Dict[str, Any]]) -> None:
        """Iterates over the data list to create products, galleries, and videos."""
        brand = self.get_or_create_brand("Global Brand")
        
        for index, item in enumerate(data):
            category = self.get_or_create_category(item.get("category", "General"))
            
            price_irt = int(float(item.get("price", 0)) * 50000)
            
            product = Product.objects.create(
                category=category,
                brand=brand,
                title=item.get("title")[:250],
                english_title=item.get("title")[:250],
                short_description=item.get("description")[:500],
                description=item.get("description"),
                base_price=price_irt,
                base_inventory=100,
                weight=500,
                volume=1000,
                is_active=True,
                average_rating=item.get("rating", {}).get("rate", 0.0),
                view_count=item.get("rating", {}).get("count", 0),
            )
            
            image_url = item.get("image")
            if image_url:
                filename = f"product_{product.uuid}.png"
                image_file = self.download_file(image_url, filename, is_image=True)
                if image_file:
                    ProductGallery.objects.create(
                        product=product,
                        image=image_file,
                        image_alt=product.title,
                        is_main=True
                    )
            
            if index % 2 == 0:
                video_file = self.download_file(self.VIDEO_URL, f"video_{product.uuid}.mp4", is_image=False)
                if video_file:
                    ProductVideo.objects.create(
                        product=product,
                        video_file=video_file,
                        title=f"Demo for {product.title}"
                    )
            
            self.stdout.write(f"Created: {product.title}")