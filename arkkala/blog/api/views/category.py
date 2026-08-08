from rest_framework import viewsets
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from blog.api.serializers.outputs.category import BlogCategorySerializer
from blog.dependencies import get_category_repository
from blog.application.queries.get_active_categories import GetActiveCategoriesUseCase

class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogCategorySerializer
    pagination_class = None
    lookup_field = 'slug'

    @extend_schema(summary="List all active blog categories")
    def get_queryset(self) -> QuerySet:
        use_case = GetActiveCategoriesUseCase(get_category_repository())
        return use_case.execute()