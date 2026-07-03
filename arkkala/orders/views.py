"""
API Views for Orders and Cart.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .services import CartService, OrderService
from .serializers import CartSerializer, OrderSerializer


class CartViewSet(viewsets.ViewSet):
    """Cart API allowing both authenticated users and guests."""
    permission_classes = [AllowAny]

    def list(self, request) -> Response:
        cart = CartService.get_or_create_cart(request)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request) -> Response:
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not variant_id:
            return Response({"detail": "شناسه محصول (Variant) الزامی است."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            CartService.add_item(request, variant_id, quantity)
            return Response({"detail": "آیتم به سبد خرید اضافه شد."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ViewSet):
    """Order API handling Checkout for both Users and Guests."""
    
    def get_permissions(self):
        if self.action in ['list', 'reorder']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def list(self, request) -> Response:
        orders = request.user.orders.all().order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)

    @action(detail=False, methods=['post'])
    def checkout(self, request) -> Response:
        # Validate guest checkout requirement
        if not request.user.is_authenticated and not request.data.get('guest_mobile'):
            return Response({"detail": "برای ثبت سفارش مهمان، وارد کردن شماره موبایل الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = OrderService.checkout(request, request.data)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "خطای پیش‌بینی نشده در ثبت سفارش."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)