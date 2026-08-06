from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from typing import Any
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from platform_seo.sitemaps import ProductSitemap, ShopCategorySitemap, PostSitemap, StaticPagesSitemap
from platform_seo.views.robot import RobotsTxtView
from .health import healthz

sitemaps: dict[str, Any] = {
    'static': StaticPagesSitemap,
    'products': ProductSitemap,
    'shop_categories': ShopCategorySitemap,
    'posts': PostSitemap,
}

urlpatterns: list[Any] = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('api/users/', include('users.urls')),
    path('api/shop/', include('shop.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/search/', include('search.urls')),
    path('api/home/', include('home.urls')),
    path('api/platform_seo/', include('platform_seo.urls')),
    path('healthz/', healthz, name='healthz'),
    
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("robots.txt", RobotsTxtView.as_view(), name="robots_txt"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)