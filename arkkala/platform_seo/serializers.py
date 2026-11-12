"""
Base SEO Serializers for Headless Architecture.
Ensures Canonical URLs and OpenGraph URLs point to the Frontend Domain.
"""
from typing import Any, Dict, Optional

from django.conf import settings
from rest_framework import serializers


class BaseSeoSerializer(serializers.ModelSerializer):
    """
    Abstract SEO Serializer to be inherited by models implementing SEOMixin and JsonLdMixin.
    """
    seo_keywords = serializers.JSONField(source='keywords', read_only=True)
    canonical_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()
    schema_markup = serializers.SerializerMethodField()

    def get_frontend_url(self, path: str) -> str:
        """
        Generates an absolute URL pointing strictly to the React frontend.
        """
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        if not path.startswith('/'):
            path = f'/{path}'
        return f"{frontend_domain}{path}"

    def get_canonical_url(self, obj: Any) -> str:
        """Must be overridden in subclasses to return specific entity path."""
        if hasattr(obj, 'og_url') and obj.og_url:
            return obj.og_url
        raise NotImplementedError("Subclasses must implement get_canonical_url")

    def _build_absolute_media_url(self, raw_url: str) -> str:
        if not raw_url:
            return ""
        if raw_url.startswith(('http://', 'https://')):
            return raw_url
        request: Optional[Any] = self.context.get('request')
        if request:
            return request.build_absolute_uri(raw_url)
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        return f"{frontend_domain}{raw_url if raw_url.startswith('/') else '/' + raw_url}"

    def get_og_image_url(self, obj: Any) -> Optional[str]:
        """
        Safely constructs the absolute URL for the OpenGraph image without N+1 queries.
        Handles both URLField (str) and ImageField/FileField instances.
        """
        og_img = getattr(obj, 'og_image', None)
        if og_img:
            raw_url = og_img.url if hasattr(og_img, 'url') else str(og_img)
            return self._build_absolute_media_url(raw_url)

        for field_name in ('image', 'logo'):
            img_field = getattr(obj, field_name, None)
            if img_field and hasattr(img_field, 'url'):
                return self._build_absolute_media_url(img_field.url)

        if hasattr(obj, 'gallery'):
            # Use .all() to leverage prefetch_related cache and prevent N+1 queries
            gallery_items = list(obj.gallery.all())
            if gallery_items:
                main_img = next((item for item in gallery_items if getattr(item, 'is_main', False)), gallery_items[0])
                if getattr(main_img, 'image', None):
                    return self._build_absolute_media_url(main_img.image.url)

        return None

    def get_schema_markup(self, obj: Any) -> Dict[str, Any]:
        """
        Fetches the generated JSON-LD from the model or falls back to custom json_ld.
        """
        if hasattr(obj, 'generate_json_ld'):
            return obj.generate_json_ld()
        if hasattr(obj, 'json_ld') and obj.json_ld:
            return obj.json_ld
        return {}