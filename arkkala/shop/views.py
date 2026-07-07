"""
API Views for Shop App.
"""
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

from .models import Product
from .serializers import ProductDetailSerializer
from .services import ProductService, QuestionService
from .filters import ProductFilter


class MaxPriceAPIView(APIView):
    """
    API View to retrieve the maximum product price for filtering bounds.
    """
    def get(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle GET request to fetch the maximum price.
        """
        max_price: int = ProductService.get_max_price()
        return Response({"max_price": max_price}, status=status.HTTP_200_OK)


class ProductPagination(PageNumberPagination):
    """
    Custom pagination for products to ensure frontend receives count, next, and previous.
    """
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving and filtering products.
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        'variants__attribute_values', 'comments', 'gallery', 'brand', 'category', 'questions'
    )
    serializer_class = ProductDetailSerializer
    pagination_class = ProductPagination 
    
    lookup_field = 'slug'
    lookup_value_regex = '[^/]+' 
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'english_title', 'description', 'short_description']
    ordering_fields = ['base_price', 'sold_count', 'view_count', 'average_rating', 'created_at']
    ordering = ['-created_at']

    def get_object(self) -> Product:
        """
        Overriding get_object to intelligently fetch by either UUID or Slug.
        This provides perfect SEO support while maintaining backward compatibility with internal IDs.
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        identifier = self.kwargs.get(lookup_url_kwarg)

        try:
            valid_uuid = uuid.UUID(identifier, version=4)
            obj = get_object_or_404(queryset, uuid=valid_uuid)
        except ValueError:
            obj = get_object_or_404(queryset, slug=identifier)

        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Override retrieve to increment view count using Service Layer."""
        instance: Product = self.get_object()
        ProductService.increment_view_count(product=instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request: Request, slug=None) -> Response:
        """Action for users to submit comments using Service Layer."""
        try:
            product: Product = self.get_object()
            body: str = request.data.get('body')
            rating: int = int(request.data.get('rating', 5))
            user = request.user if request.user.is_authenticated else None
            
            ProductService.add_comment(
                product=product,
                user=user,
                body=body,
                rating=rating
            )
            return Response(
                {"message": "دیدگاه شما ثبت شد و پس از بررسی نمایش داده می‌شود."}, 
                status=status.HTTP_201_CREATED
            )
        except ValueError:
            return Response({"error": "فرمت مقادیر ارسال شده نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def add_question(self, request: Request, slug=None) -> Response:
        """
        Public API action allowing anyone (including guests) to drop a question.
        """
        try:
            product: Product = self.get_object()
            text: Optional[str] = request.data.get('text')
            name: Optional[str] = request.data.get('name', 'کاربر مهمان')

            if not text or not text.strip():
                return Response({"error": "متن پرسش نمی‌تواند خالی باشد."}, status=status.HTTP_400_BAD_REQUEST)

            QuestionService.add_question(
                product=product,
                text=text,
                user=request.user,
                name=name
            )
            return Response(
                {"message": "پرسش شما با موفقیت ثبت شد و پس از بررسی و تایید نمایش داده می‌شود."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request: Request, slug=None) -> Response:
        """
        API Action to add/remove a product from user's favorites completely via Service Layer.
        """
        try:
            product: Product = self.get_object()
            user = request.user
            
            # Delegate logic to ProductService
            result = ProductService.toggle_favorite(product=product, user=user)
            
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)