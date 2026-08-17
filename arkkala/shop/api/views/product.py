import uuid
from typing import Any, Optional
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from shop.models.product import Product
from shop.api.serializers.outputs.product import ProductDetailSerializer
from shop.api.serializers.inputs.interaction import CreateCommentInputSerializer, CreateQuestionInputSerializer
from shop.api.filters import ProductFilter
from shop.api.pagination import ProductPagination
from shop.api.exceptions import exception_handler_wrapper
from shop.application.dto.commands import CreateCommentCommandDTO, CreateQuestionCommandDTO, TrackProductViewDTO

import shop.dependencies as deps

class MaxPriceAPIView(APIView):
    @extend_schema(summary="Get maximum base price")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        query = deps.get_max_price_query()
        return Response({"max_price": query.execute()}, status=status.HTTP_200_OK)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductDetailSerializer
    pagination_class = ProductPagination 
    lookup_field = 'slug'
    lookup_value_regex = '[^/]+' 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'english_title', 'description', 'short_description']
    ordering_fields = ['base_price', 'sold_count', 'view_count', 'average_rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self) -> Any:
        query = deps.get_optimized_products_query()
        return query.execute(self.request.user)

    def get_object(self) -> Product:
        queryset = self.filter_queryset(self.get_queryset())
        identifier = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        try:
            obj = get_object_or_404(queryset, uuid=uuid.UUID(identifier, version=4))
        except ValueError:
            obj = get_object_or_404(queryset, slug=identifier)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(summary="Retrieve a product and track view history")
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        slug = self.kwargs.get(self.lookup_field)
        
        user_id = request.user.id if request.user and request.user.is_authenticated else None
        guest_id = request.headers.get('X-Guest-ID')
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR')
        
        viewer_id = str(user_id) if user_id else (guest_id or client_ip)
        cache_key = f"product_view_lock_{slug}_{viewer_id}"

        if not cache.get(cache_key):
            command = deps.get_increment_view_count_command()
            command.execute(slug)

            if user_id or guest_id:
                track_command = deps.get_track_product_view_command()
                track_dto = TrackProductViewDTO(user_id=user_id, guest_id=guest_id, product_slug=slug)
                track_command.execute(track_dto)
            
            cache.set(cache_key, True, timeout=5)

        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary="Get user's favorite products")
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request: Request) -> Response:
        queryset = self.filter_queryset(self.get_queryset().filter(favorites=request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @extend_schema(summary="Get personalized product recommendations based on identity history")
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def recommendations(self, request: Request) -> Response:
        guest_id = request.headers.get('X-Guest-ID')
        query = deps.get_product_recommendations_query()
        
        queryset = query.execute(request.user, guest_id)
        
        return Response(self.get_serializer(queryset, many=True).data)

    @extend_schema(summary="Toggle product favorite status")
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    @exception_handler_wrapper
    def toggle_favorite(self, request: Request, slug: Optional[str] = None) -> Response:
        command = deps.get_toggle_favorite_command()
        result = command.execute(slug, request.user.id)
        return Response(result, status=status.HTTP_200_OK)

    @extend_schema(summary="Add a comment to a product")
    @action(detail=True, methods=['post'])
    @exception_handler_wrapper
    def add_comment(self, request: Request, slug: Optional[str] = None) -> Response:
        serializer = CreateCommentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dto = CreateCommentCommandDTO(
            product_slug=slug,
            body=serializer.validated_data['body'],
            rating=serializer.validated_data['rating'],
            user_id=request.user.id if request.user.is_authenticated else None
        )
        
        command = deps.get_create_comment_command()
        command.execute(dto)
        return Response({"message": "دیدگاه شما ثبت شد و پس از بررسی نمایش داده می‌شود."}, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Ask a question about a product")
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    @exception_handler_wrapper
    def add_question(self, request: Request, slug: Optional[str] = None) -> Response:
        serializer = CreateQuestionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = CreateQuestionCommandDTO(
            product_slug=slug,
            body=serializer.validated_data['text'],
            user_id=request.user.id if request.user.is_authenticated else None,
            guest_name=serializer.validated_data.get('name', 'کاربر مهمان')
        )
        
        command = deps.get_create_question_command()
        command.execute(dto)
        return Response({"message": "پرسش شما با موفقیت ثبت شد."}, status=status.HTTP_201_CREATED)