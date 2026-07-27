# shop/views/product.py
import uuid
from typing import Optional
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from shop.models.product import Product
from shop.serializers.product import ProductDetailSerializer
from shop.services.product import ProductService
from shop.services.interaction import InteractionService
from shop.filters import ProductFilter


class MaxPriceAPIView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        return Response({"max_price": ProductService.get_max_price()}, status=status.HTTP_200_OK)


class ProductPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100


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

    def get_queryset(self):
        return Product.objects.active().with_relations().with_approved_feedback().with_user_favorite(self.request.user)

    def get_object(self) -> Product:
        queryset = self.filter_queryset(self.get_queryset())
        identifier = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)

        try:
            obj = get_object_or_404(queryset, uuid=uuid.UUID(identifier, version=4))
        except ValueError:
            obj = get_object_or_404(queryset, slug=identifier)

        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        ProductService.increment_view_count(product=instance)
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request: Request) -> Response:
        queryset = self.get_queryset().filter(favorites=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request: Request, slug=None) -> Response:
        try:
            return Response(ProductService.toggle_favorite(product=self.get_object(), user=request.user), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_comment(self, request: Request, slug=None) -> Response:
        try:
            InteractionService.add_comment(
                product=self.get_object(),
                user=request.user if request.user.is_authenticated else None,
                body=request.data.get('body'),
                rating=int(request.data.get('rating', 5))
            )
            return Response({"message": "دیدگاه شما ثبت شد و پس از بررسی نمایش داده می‌شود."}, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({"error": "فرمت مقادیر ارسال شده نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def add_question(self, request: Request, slug=None) -> Response:
        try:
            text: Optional[str] = request.data.get('text')
            if not text or not text.strip():
                return Response({"error": "متن پرسش نمی‌تواند خالی باشد."}, status=status.HTTP_400_BAD_REQUEST)

            InteractionService.add_question(
                product=self.get_object(),
                text=text,
                user=request.user,
                name=request.data.get('name', 'کاربر مهمان')
            )
            return Response({"message": "پرسش شما با موفقیت ثبت شد و پس از بررسی و تایید نمایش داده می‌شود."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)