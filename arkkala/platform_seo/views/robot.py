"""
Dynamic robots.txt and llms.txt generator for SEO, AEO, and GEO.
"""
from typing import Any, List
from django.conf import settings
from django.http import HttpResponse
from django.views.generic.base import View

from platform_seo.models import RobotsTxt
from shop.models import Brand, Category, Product


def resolve_frontend_domain(request: Any) -> str:
    """Returns the active frontend origin for dev/staging or FRONTEND_URL for production."""
    host = request.get_host() if request else ''
    if host and not host.startswith(('api.', 'django', 'nginx')):
        scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
        return f"{scheme}://{host}".rstrip('/')
    return getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')


class RobotsTxtView(View):
    """Generates robots.txt optimized for Search Engines, Shopping Bots (Torob/Emalls), and AI/GEO Crawlers."""

    def get(self, request: Any, *args: tuple, **kwargs: dict) -> HttpResponse:
        obj: RobotsTxt | None = RobotsTxt.objects.first()
        frontend_domain: str = resolve_frontend_domain(request)
        header_lines: str = (
            f"Sitemap: {frontend_domain}/sitemap.xml\n"
            f"# GEO / AI Knowledge Index\n"
            f"# LLMs-Txt: {frontend_domain}/llms.txt\n"
            f"# LLMs-Full-Txt: {frontend_domain}/llms-full.txt\n\n"
        )

        if obj and obj.content and obj.content.strip():
            content: str = header_lines + obj.content.strip() + "\n"
        else:
            default_rules = [
                "User-agent: *",
                "Allow: /",
                "Disallow: /admin/",
                "Disallow: /dashboard/",
                "Disallow: /cart",
                "Disallow: /checkout",
                "Disallow: /login",
                "Disallow: /payment/",
                "",
                "# AI & Answer Engine Crawlers (AEO / GEO)",
                "User-agent: OAI-SearchBot",
                "Allow: /",
                "",
                "User-agent: ChatGPT-User",
                "Allow: /",
                "",
                "User-agent: PerplexityBot",
                "Allow: /",
                "",
                "User-agent: ClaudeBot",
                "Allow: /",
                "",
                "User-agent: Google-Extended",
                "Allow: /",
                "",
                "# Iranian Price Comparison Crawlers",
                "User-agent: torob",
                "Allow: /",
                "",
                "User-agent: emalls",
                "Allow: /",
            ]
            content = header_lines + "\n".join(default_rules) + "\n"

        return HttpResponse(content, content_type="text/plain; charset=utf-8")


class LlmsTxtView(View):
    """
    Generates /llms.txt and /llms-full.txt according to the llms.txt standard for GEO.
    """
    full_detail: bool = False

    def get(self, request: Any, *args: tuple, **kwargs: dict) -> HttpResponse:
        frontend_domain: str = resolve_frontend_domain(request)
        site_name: str = getattr(settings, 'SITE_NAME', 'ارک کالا')

        categories = Category.objects.filter(is_active=True).order_by('order')[:30]
        brands = Brand.objects.filter(is_active=True)[:30]
        products_qs = (
            Product.objects.active()
            .select_related('category', 'brand')
            .prefetch_related('questions')
            .order_by('-sold_count', '-view_count')
        )
        products = list(products_qs[:100] if self.full_detail else products_qs[:25])

        lines: List[str] = [
            f"# {site_name} (Arkkala E-Commerce Platform)",
            "",
            f"> فروشگاه اینترنتی {site_name}؛ مرجع تخصصی بررسی، مقایسه و خرید آنلاین کالا با تضمین اصالت و گارانتی معتبر.",
            "",
            "## لینک‌های اصلی (Core Navigation)",
            f"- [صفحه اصلی]({frontend_domain}/)",
            f"- [فروشگاه محصولات]({frontend_domain}/shop)",
            f"- [پیشنهادهای شگفت‌انگیز]({frontend_domain}/special-offers)",
            f"- [پرفروش‌ترین‌ها]({frontend_domain}/best-sellers)",
            f"- [مجله و مقالات تخصصی]({frontend_domain}/blog)",
            f"- [سوالات متداول]({frontend_domain}/faq)",
            f"- [درباره ما]({frontend_domain}/about)",
            f"- [تماس با ما]({frontend_domain}/contact)",
            f"- [نقشه سایت XML]({frontend_domain}/sitemap.xml)",
            "",
        ]

        if categories:
            lines.append("## دسته‌بندی‌های محصولات (Product Categories)")
            for cat in categories:
                desc = f": {cat.meta_description}" if cat.meta_description else ""
                lines.append(f"- [{cat.title}]({frontend_domain}/category/{cat.slug}){desc}")
            lines.append("")

        if brands:
            lines.append("## برندهای رسمی (Official Brands)")
            for brand in brands:
                lines.append(f"- [{brand.title}]({frontend_domain}/shop?brands={brand.slug})")
            lines.append("")

        if products:
            lines.append("## محصولات شاخص و مشخصات کلیدی (Featured Products & GEO Data)")
            for p in products:
                status_str = "موجود (In Stock)" if p.base_inventory > 0 else "ناموجود (Out of Stock)"
                lines.append(f"### [{p.title}]({frontend_domain}/product/{p.slug})")
                lines.append(f"- **قیمت فعلی:** {p.final_price:,} تومان | **وضعیت:** {status_str}")
                if p.brand:
                    lines.append(f"- **برند:** {p.brand.title}")
                if p.category:
                    lines.append(f"- **دسته‌بندی:** {p.category.title}")
                if p.average_rating > 0:
                    lines.append(f"- **امتیاز کاربران:** {p.average_rating:.1f} از 5")
                if p.expert_reviewer:
                    lines.append(f"- **بررسی‌کننده تخصصی (E-E-A-T):** {p.expert_reviewer}")
                if p.key_takeaways and isinstance(p.key_takeaways, list):
                    takeaways = "، ".join(str(k) for k in p.key_takeaways if k)
                    if takeaways:
                        lines.append(f"- **نکات کلیدی (Key Takeaways):** {takeaways}")
                if p.citations and isinstance(p.citations, list):
                    cites = "، ".join(str(c) for c in p.citations if c)
                    if cites:
                        lines.append(f"- **منابع (Citations):** {cites}")
                if self.full_detail:
                    if p.short_description:
                        lines.append(f"- **خلاصه بررسی:** {p.short_description}")
                    answered_qs = [
                        q for q in p.questions.all()
                        if q.is_approved and q.answer_text and q.answer_text.strip()
                    ]
                    if answered_qs:
                        lines.append("- **پرسش و پاسخ‌های متداول (AEO Q&A):**")
                        for q in answered_qs[:5]:
                            lines.append(f"  - *سوال:* {q.text}")
                            lines.append(f"    *پاسخ:* {q.answer_text}")
                lines.append("")

        return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")