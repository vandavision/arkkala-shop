from rest_framework import viewsets
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from blog.serializers.category import BlogCategorySerializer
from blog.application.queries.category import CategoryQueryService

class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Thin routing integration completely delegating DB extractions.
    """
    serializer_class = BlogCategorySerializer
    pagination_class = None
    lookup_field: str = 'slug'

    @extend_schema(summary="List all active blog categories")
    def get_queryset(self) -> QuerySet:
        """
        Receives validated records dynamically through specific Query interface safely.
        """
        return CategoryQueryService.get_active_categories()