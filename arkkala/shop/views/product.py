import uuid
from typing import Optional, Any
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from shop.models.product import Product
from shop.serializers.product import ProductDetailSerializer
from shop.application.queries.product import ProductQueryService
from shop.application.commands.product import ProductCommandService
from shop.application.commands.interaction import InteractionCommandService
from shop.application.dtos import InteractionCreateDTO
from shop.filters import ProductFilter

class MaxPriceAPIView(APIView):
    """
    Retrieve the maximum product price dynamically from Cache Strategy.
    """
    @extend_schema(summary="Get maximum base price", responses={200: OpenApiResponse(description='Max Price')})
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return Response({"max_price": ProductQueryService.get_max_price()}, status=status.HTTP_200_OK)

class ProductPagination(PageNumberPagination):
    page_size: int = 9
    page_size_query_param: str = 'page_size'
    max_page_size: int = 100

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Enterprise ViewSet using CQRS architecture.
    """
    serializer_class = ProductDetailSerializer
    pagination_class = ProductPagination 
    lookup_field: str = 'slug'
    lookup_value_regex: str = '[^/]+' 
    filter_backends: list = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields: list = ['title', 'english_title', 'description', 'short_description']
    ordering_fields: list = ['base_price', 'sold_count', 'view_count', 'average_rating', 'created_at']
    ordering: list = ['-created_at']

    def get_queryset(self) -> Any:
        return ProductQueryService.get_optimized_products(self.request.user)

    def get_object(self) -> Product:
        queryset = self.filter_queryset(self.get_queryset())
        identifier = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        try:
            obj = get_object_or_404(queryset, uuid=uuid.UUID(identifier, version=4))
        except ValueError:
            obj = get_object_or_404(queryset, slug=identifier)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(summary="Retrieve a product and increment view count atomically")
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # Fire-and-forget Atomic write command
        ProductCommandService.increment_view_count(self.kwargs.get(self.lookup_field))
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Get user's favorite products")
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request: Request) -> Response:
        queryset: Any = self.get_queryset().filter(favorites=request.user)
        page: Any = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @extend_schema(summary="Toggle product favorite status")
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request: Request, slug: Optional[str] = None) -> Response:
        try:
            result = ProductCommandService.toggle_favorite(slug, request.user.id)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(summary="Add a comment to a product")
    @action(detail=True, methods=['post'])
    def add_comment(self, request: Request, slug: Optional[str] = None) -> Response:
        try:
            dto = InteractionCreateDTO(
                product_slug=slug,
                user_id=request.user.id if request.user.is_authenticated else None,
                body=request.data.get('body', ''),
                rating=int(request.data.get('rating', 5))
            )
            InteractionCommandService.create_comment(dto)
            return Response({"message": "دیدگاه شما ثبت شد و پس از بررسی نمایش داده می‌شود."}, status=status.HTTP_201_CREATED)
        except (ValueError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Ask a question about a product")
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def add_question(self, request: Request, slug: Optional[str] = None) -> Response:
        try:
            dto = InteractionCreateDTO(
                product_slug=slug,
                user_id=request.user.id if request.user.is_authenticated else None,
                body=request.data.get('text', ''),
                name=request.data.get('name', 'کاربر مهمان')
            )
            InteractionCommandService.create_question(dto)
            return Response({"message": "پرسش شما با موفقیت ثبت شد."}, status=status.HTTP_201_CREATED)
        except (ValueError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)