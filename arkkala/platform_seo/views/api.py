"""
API View for Static Pages Meta Information.
"""
from typing import Any, Dict

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from platform_seo.models import MetaInformation


class StaticPageSeoAPIView(APIView):
    """
    API View to fetch SEO MetaInformation for static React routes 
    (e.g., HomePage, AboutUsPage).
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        """
        Handles GET requests to return SEO data for a specific static view.
        
        Args:
            request (Request): The incoming request containing 'view_name' param.
            
        Returns:
            Response: JSON response containing SEO parameters.
        """
        view_name: str = request.query_params.get('view_name', '').strip()
        if not view_name:
            return Response({"error": "view_name parameter is required"}, status=400)

        meta: MetaInformation | None = MetaInformation.objects.filter(view_name__iexact=view_name).first()
        if not meta:
            return Response({}, status=200)

        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        canonical: str = meta.canonical_url
        
        if canonical and canonical.startswith('/'):
            canonical = f"{frontend_domain}{canonical}"

        data: Dict[str, Any] = {
            'title': meta.title,
            'meta_description': meta.description,
            'seo_keywords': meta.keywords,
            'canonical_url': canonical,
            'schema_markup': meta.json_ld,
            'robots': f"{'index' if meta.index_page else 'noindex'}, {'follow' if meta.follow_page_links else 'nofollow'}"
        }
        
        return Response(data, status=200)