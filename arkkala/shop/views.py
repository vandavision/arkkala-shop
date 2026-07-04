"""
API Views for Shop App.
"""
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductDetailSerializer
from .services import ProductService
from .filters import ProductFilter


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving and filtering products.
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        'variants__attribute_values', 'comments', 'gallery', 'brand', 'category'
    )
    serializer_class = ProductDetailSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'english_title', 'description', 'short_description']
    ordering_fields = ['base_price', 'sold_count', 'view_count', 'average_rating', 'created_at']
    ordering = ['-created_at']

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Override retrieve to increment view count using Service Layer."""
        instance: Product = self.get_object()
        ProductService.increment_view_count(product=instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request: Request, pk=None) -> Response:
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