"""
Dynamic XML Sitemaps targeting Frontend URLs for Headless SEO.
"""
from typing import Any, List
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap

from blog.models import Post
from shop.models import Brand, Category as ShopCategory, Product


class BaseFrontendSitemap(Sitemap):
    """
    Base sitemap that dynamically matches the active frontend host in dev/staging
    and enforces FRONTEND_URL when accessed via api.* or internal containers.
    """

    def get_urls(self, page: int = 1, site: Any = None, protocol: Any = None) -> list:
        frontend_url: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com')
        parsed = urlparse(frontend_url)

        req_domain: str = getattr(site, 'domain', '') if site else ''
        is_internal_or_api: bool = (
            not req_domain
            or req_domain.startswith('api.')
            or req_domain.startswith('django')
            or req_domain.startswith('nginx')
        )

        if is_internal_or_api:
            target_domain = parsed.netloc or 'arkkala.com'
            target_protocol = parsed.scheme or 'https'
        else:
            target_domain = req_domain
            target_protocol = protocol or 'http'

        class ResolvedSite:
            domain = target_domain

        return super().get_urls(page=page, site=ResolvedSite(), protocol=target_protocol)


class ProductSitemap(BaseFrontendSitemap):
    changefreq: str = "daily"
    priority: float = 0.9

    def items(self) -> Any:
        return Product.objects.filter(is_active=True).order_by('-modified_at')

    def lastmod(self, obj: Product) -> Any:
        return obj.modified_at

    def location(self, obj: Product) -> str:
        return f"/product/{obj.slug}"


class ShopCategorySitemap(BaseFrontendSitemap):
    changefreq: str = "weekly"
    priority: float = 0.8

    def items(self) -> Any:
        return ShopCategory.objects.filter(is_active=True).order_by('-modified_at')

    def lastmod(self, obj: ShopCategory) -> Any:
        return obj.modified_at

    def location(self, obj: ShopCategory) -> str:
        return f"/category/{obj.slug}"


class BrandSitemap(BaseFrontendSitemap):
    changefreq: str = "weekly"
    priority: float = 0.7

    def items(self) -> Any:
        return Brand.objects.filter(is_active=True).order_by('-modified_at')

    def lastmod(self, obj: Brand) -> Any:
        return obj.modified_at

    def location(self, obj: Brand) -> str:
        return f"/shop?brands={obj.slug}"


class PostSitemap(BaseFrontendSitemap):
    changefreq: str = "weekly"
    priority: float = 0.8

    def items(self) -> Any:
        return Post.objects.filter(is_published=True).order_by('-modified_at')

    def lastmod(self, obj: Post) -> Any:
        return getattr(obj, 'modified_at', getattr(obj, 'updated_at', None))

    def location(self, obj: Post) -> str:
        return f"/blog/{obj.slug}"


class StaticPagesSitemap(BaseFrontendSitemap):
    changefreq: str = "weekly"
    priority: float = 1.0

    def items(self) -> List[str]:
        return [
            '/',
            '/shop',
            '/special-offers',
            '/best-sellers',
            '/categories',
            '/brands',
            '/blog',
            '/faq',
            '/about',
            '/contact',
            '/rules',
            '/return',
        ]

    def location(self, item: str) -> str:
        return item