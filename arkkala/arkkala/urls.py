"""
Main URL configuration for arkkala.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from typing import Any

from platform_seo.sitemaps import ProductSitemap, ShopCategorySitemap, PostSitemap, StaticPagesSitemap

sitemaps: dict[str, Any] = {
    'static': StaticPagesSitemap,
    'products': ProductSitemap,
    'shop_categories': ShopCategorySitemap,
    'posts': PostSitemap,
}

urlpatterns: list[Any] = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/shop/', include('shop.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/search/', include('search.urls')),
    path('api/home/', include('home.urls')),
    path('api/platform_seo/', include('platform_seo.urls')),
    
    # Sitemap Route
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)