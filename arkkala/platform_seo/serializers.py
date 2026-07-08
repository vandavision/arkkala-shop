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
        
        Args:
            path (str): The relative path (e.g., '/product/slug/').
            
        Returns:
            str: The absolute URL.
        """
        frontend_domain: str = getattr(settings, 'FRONTEND_URL', 'https://arkkala.com').rstrip('/')
        if not path.startswith('/'):
            path = f'/{path}'
        return f"{frontend_domain}{path}"

    def get_canonical_url(self, obj: Any) -> str:
        """Must be overridden in subclasses to return specific entity path."""
        raise NotImplementedError("Subclasses must implement get_canonical_url")

    def get_og_image_url(self, obj: Any) -> Optional[str]:
        """
        Constructs the absolute URL for the OpenGraph image pointing to the Backend Media Server.
        
        Args:
            obj (Any): The model instance.
            
        Returns:
            Optional[str]: The absolute image URL or None.
        """
        request: Optional[Any] = self.context.get('request')
        
        if hasattr(obj, 'og_image') and obj.og_image:
            return request.build_absolute_uri(obj.og_image.url) if request else obj.og_image.url
        
        if hasattr(obj, 'image') and obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
            
        if hasattr(obj, 'gallery') and obj.gallery.exists():
            main_img = obj.gallery.filter(is_main=True).first() or obj.gallery.first()
            return request.build_absolute_uri(main_img.image.url) if request else main_img.image.url
            
        return None

    def get_schema_markup(self, obj: Any) -> Dict[str, Any]:
        """
        Fetches the generated JSON-LD from the model.
        
        Args:
            obj (Any): The model instance.
            
        Returns:
            Dict[str, Any]: The structured schema dictionary.
        """
        return obj.generate_json_ld() if hasattr(obj, 'generate_json_ld') else {}