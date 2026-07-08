"""
Dynamic XML Sitemaps targeting Frontend URLs for Headless SEO.
"""
from typing import Any, List
from urllib.parse import urlparse

from django.contrib.sitemaps import Sitemap
from django.conf import settings

# FIX: Import Category from 'shop', not 'search'
from shop.models import Product, Category as ShopCategory
from blog.models import Post, Category as BlogCategory


class BaseFrontendSitemap(Sitemap):
    """Base sitemap that forces protocol and domain to frontend settings."""
    
    def get_urls(self, page: int = 1, site: Any = None, protocol: Any = None) -> list:
        frontend_url: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com')
        parsed = urlparse(frontend_url)
        
        class MockSite:
            domain = parsed.netloc

        return super().get_urls(page=page, site=MockSite(), protocol=parsed.scheme)


class ProductSitemap(BaseFrontendSitemap):
    changefreq: str = "daily"
    priority: float = 0.9

    def items(self) -> Any:
        return Product.objects.filter(is_active=True).order_by('-modified_at')

    def lastmod(self, obj: Product) -> Any:
        return obj.modified_at

    def location(self, obj: Product) -> str:
        return f"/product/{obj.slug}/"


class ShopCategorySitemap(BaseFrontendSitemap):
    changefreq: str = "weekly"
    priority: float = 0.8

    def items(self) -> Any:
        return ShopCategory.objects.filter(is_active=True).order_by('-modified_at')

    def lastmod(self, obj: ShopCategory) -> Any:
        return obj.modified_at

    def location(self, obj: ShopCategory) -> str:
        return f"/category/{obj.slug}/"


class PostSitemap(BaseFrontendSitemap):
    changefreq: str = "weekly"
    priority: float = 0.8

    def items(self) -> Any:
        return Post.objects.filter(is_published=True).order_by('-modified_at')

    def lastmod(self, obj: Post) -> Any:
        return obj.modified_at

    def location(self, obj: Post) -> str:
        return f"/blog/{obj.slug}/"


class StaticPagesSitemap(BaseFrontendSitemap):
    changefreq: str = "monthly"
    priority: float = 1.0

    def items(self) -> List[str]:
        return ['/', '/shop', '/blog', '/about', '/faq', '/contact']

    def location(self, item: str) -> str:
        return item