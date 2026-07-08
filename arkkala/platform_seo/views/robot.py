"""
Dynamic robots.txt generator.
"""
from typing import Any

from django.http import HttpResponse
from django.views.generic.base import View
from django.conf import settings

from platform_seo.models import RobotsTxt


class RobotsTxtView(View):
    """Generates the robots.txt content, appending the Frontend Sitemap URL."""
    
    def get(self, request: Any, *args: tuple, **kwargs: dict) -> HttpResponse:
        obj: RobotsTxt | None = RobotsTxt.objects.first()
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        sitemap_url: str = f"Sitemap: {frontend_domain}/sitemap.xml\n\n"

        if obj and obj.content:
            content: str = sitemap_url + obj.content
        else:
            content: str = sitemap_url + "User-agent: *\nDisallow: /admin/\nAllow: /"
            
        return HttpResponse(content, content_type="text/plain")