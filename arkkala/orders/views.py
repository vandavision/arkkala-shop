"""
Views for Orders and Cart.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from .models import CartItem, Order, ShippingMethod
from .serializers import (
    CartItemSerializer, OrderSerializer, CheckoutSerializer, ShippingMethodSerializer
)
from .services import CartService, OrderService


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """List available shipping methods."""
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer


class CartViewSet(viewsets.ViewSet):
    """Manage User Cart."""
    permission_classes = [IsAuthenticated]

    def list(self, request: Request) -> Response:
        cart = CartService.get_user_cart(request.user)
        serializer = CartItemSerializer(cart.items.all(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request: Request) -> Response:
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CartService.add_to_cart(
            user=request.user,
            product_id=serializer.validated_data['product'].id,
            variant_id=serializer.validated_data.get('variant').id if serializer.validated_data.get('variant') else None,
            quantity=serializer.validated_data.get('quantity', 1)
        )
        return Response({"message": "به سبد خرید اضافه شد."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request: Request, pk=None) -> Response:
        quantity = request.data.get('quantity')
        CartService.update_item_quantity(pk, request.user, int(quantity))
        return Response({"message": "تعداد بروزرسانی شد."})

    @action(detail=True, methods=['delete'])
    def remove(self, request: Request, pk=None) -> Response:
        CartService.remove_item(pk, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """User Orders and Checkout process."""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def checkout(self, request: Request) -> Response:
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        address_data = {
            'title': serializer.validated_data['title'],
            'country': serializer.validated_data['country'],
            'province': serializer.validated_data['province'],
            'city': serializer.validated_data['city'],
            'postal_address': serializer.validated_data['postal_address'],
            'postal_code': serializer.validated_data['postal_code'],
            'plaque': serializer.validated_data['plaque'],
            'building_unit': serializer.validated_data.get('building_unit', ''),
        }
        
        try:
            order = OrderService.checkout(
                user=request.user,
                address_data=address_data,
                shipping_method_id=serializer.validated_data['shipping_method_id'],
                coupon_code=serializer.validated_data.get('coupon_code')
            )
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)