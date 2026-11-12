"""
API View for Static Pages Meta Information with Intelligent Fallbacks.
"""
from typing import Any, Dict

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from platform_seo.models import MetaInformation


DEFAULT_STATIC_SEO_MAP: Dict[str, Dict[str, Any]] = {
    'HomePage': {
        'title': 'فروشگاه اینترنتی ارک کالا | خرید آنلاین با تضمین بهترین قیمت',
        'description': 'مرجع تخصصی بررسی، مقایسه و خرید آنلاین انواع کالا با گارانتی اصالت، ارسال سریع و پشتیبانی تخصصی در فروشگاه اینترنتی ارک کالا.',
        'keywords': ['فروشگاه اینترنتی', 'ارک کالا', 'خرید آنلاین', 'بهترین قیمت'],
        'path': '/',
        'schema_type': 'WebPage',
    },
    'ShopPage': {
        'title': 'فروشگاه محصولات | لیست قیمت و خرید آنلاین - ارک کالا',
        'description': 'مشاهده قیمت روز، مقایسه مشخصات فنی و خرید آنلاین تمامی محصولات با تضمین اصالت کالا و ارسال سریع در ارک کالا.',
        'keywords': ['لیست قیمت', 'خرید محصولات', 'فروشگاه ارک کالا'],
        'path': '/shop',
        'schema_type': 'CollectionPage',
    },
    'BlogPage': {
        'title': 'مجله تخصصی ارک کالا | نقد و بررسی و راهنمای خرید',
        'description': 'جدیدترین مقالات تخصصی، راهنمای خرید، مقایسه محصولات و اخبار تکنولوژی در مجله اینترنتی ارک کالا.',
        'keywords': ['مجله ارک کالا', 'راهنمای خرید', 'نقد و بررسی'],
        'path': '/blog',
        'schema_type': 'CollectionPage',
    },
    'FaqPage': {
        'title': 'سوالات متداول | مرکز پشتیبانی ارک کالا',
        'description': 'پاسخ به پرسش‌های متداول درباره نحوه ثبت سفارش، روش‌های ارسال، شرایط گارانتی و بازگشت کالا در ارک کالا.',
        'keywords': ['سوالات متداول', 'پشتیبانی ارک کالا', 'رهگیری سفارش'],
        'path': '/faq',
        'schema_type': 'FAQPage',
    },
    'AboutUsPage': {
        'title': 'درباره ما | آشنایی با فروشگاه اینترنتی ارک کالا',
        'description': 'آشنایی با داستان شکل‌گیری، ارزش‌ها، مجوزهای رسمی و تیم تخصصی فروشگاه اینترنتی ارک کالا.',
        'keywords': ['درباره ارک کالا', 'تماس با ارک کالا', 'اعتبار ارک کالا'],
        'path': '/about',
        'schema_type': 'AboutPage',
    },
    'ContactPage': {
        'title': 'تماس با ما | ارتباط با پشتیبانی ارک کالا',
        'description': 'راه‌های ارتباطی، شماره تماس، آدرس و فرم ارتباط مستقیم با واحد پشتیبانی و فروش ارک کالا.',
        'keywords': ['تماس با ما', 'پشتیبانی ارک کالا', 'آدرس ارک کالا'],
        'path': '/contact',
        'schema_type': 'ContactPage',
    },
    'BrandsPage': {
        'title': 'برندهای معتبر | خرید بر اساس برند در ارک کالا',
        'description': 'لیست کامل برندهای معتبر و رسمی موجود در فروشگاه اینترنتی ارک کالا همراه با تضمین اصالت کالا.',
        'keywords': ['برندها', 'نمایندگی رسمی', 'ارک کالا'],
        'path': '/brands',
        'schema_type': 'CollectionPage',
    },
    'CategoriesPage': {
        'title': 'دسته‌بندی کالاها | فروشگاه اینترنتی ارک کالا',
        'description': 'مشاهده کامل دسته‌بندی‌های محصولات فروشگاه اینترنتی ارک کالا برای دسترسی سریع و مقایسه هوشمندانه.',
        'keywords': ['دسته بندی محصولات', 'فهرست کالاها', 'ارک کالا'],
        'path': '/categories',
        'schema_type': 'CollectionPage',
    },
}


class StaticPageSeoAPIView(APIView):
    """
    API View to fetch SEO MetaInformation for static React routes
    (e.g., HomePage, AboutUsPage) with automatic structured fallbacks.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        view_name: str = request.query_params.get('view_name', '').strip()
        if not view_name:
            return Response({"error": "view_name parameter is required"}, status=400)

        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        meta: MetaInformation | None = MetaInformation.objects.filter(view_name__iexact=view_name).first()

        if meta:
            canonical: str = meta.canonical_url
            if canonical and canonical.startswith('/'):
                canonical = f"{frontend_domain}{canonical}"

            data: Dict[str, Any] = {
                'title': meta.title,
                'meta_description': meta.description,
                'seo_keywords': meta.keywords,
                'canonical_url': canonical,
                'schema_markup': meta.json_ld,
                'robots': f"{'index' if meta.index_page else 'noindex'}, {'follow' if meta.follow_page_links else 'nofollow'}",
                'modified_at': meta.modified_at.isoformat() if meta.modified_at else None,
            }
            return Response(data, status=200)

        fallback = DEFAULT_STATIC_SEO_MAP.get(view_name)
        if fallback:
            canonical_url = f"{frontend_domain}{fallback['path']}"
            return Response({
                'title': fallback['title'],
                'meta_description': fallback['description'],
                'seo_keywords': fallback['keywords'],
                'canonical_url': canonical_url,
                'schema_markup': {
                    '@context': 'https://schema.org',
                    '@type': fallback['schema_type'],
                    'name': fallback['title'],
                    'description': fallback['description'],
                    'url': canonical_url,
                },
                'robots': 'index, follow',
            }, status=200)

        return Response({}, status=200)