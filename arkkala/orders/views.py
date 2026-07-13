from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from .models import Order, ShippingMethod
from shop.models import Comment, Question
from .serializers import (
    CartItemSerializer, OrderSerializer, CheckoutSerializer, ShippingMethodSerializer
)
from .services import CartService, OrderService


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """List available shipping methods."""
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [AllowAny]


class CartViewSet(viewsets.ViewSet):
    """Manage User & Guest Cart."""
    permission_classes = [AllowAny]

    def get_guest_id(self, request: Request) -> str:
        return request.headers.get('X-Guest-ID')

    def list(self, request: Request) -> Response:
        """List items inside the cart with extensive Prefetch logic for performance."""
        guest_id = self.get_guest_id(request)
        user = request.user
        
        if not user.is_authenticated and not guest_id:
            return Response([])

        cart = CartService.get_or_create_cart(user=user if user.is_authenticated else None, guest_id=guest_id)
        
        items = cart.items.select_related(
            'product', 'product__brand', 'product__category', 'variant'
        ).prefetch_related(
            'variant__attribute_values',
            'product__variants__attribute_values',
            'product__gallery',
            'product__videos',
            'product__price_history',
            Prefetch('product__comments', queryset=Comment.objects.filter(is_approved=True), to_attr='approved_comments'),
            Prefetch('product__questions', queryset=Question.objects.filter(is_approved=True), to_attr='approved_questions')
        ).all()

        serializer = CartItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request: Request) -> Response:
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        guest_id = self.get_guest_id(request)
        if not request.user.is_authenticated and not guest_id:
            return Response({"error": "شناسه دستگاه شما مشخص نیست."}, status=status.HTTP_400_BAD_REQUEST)

        product_instance = serializer.validated_data['product']
        variant_instance = serializer.validated_data.get('variant')

        CartService.add_to_cart(
            user=request.user if request.user.is_authenticated else None,
            guest_id=guest_id,
            product_id=product_instance.pk,
            variant_id=variant_instance.pk if variant_instance else None,
            quantity=serializer.validated_data.get('quantity', 1)
        )
        return Response({"message": "به سبد خرید اضافه شد."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request: Request, pk=None) -> Response:
        quantity = request.data.get('quantity')
        CartService.update_item_quantity(pk, int(quantity), user=request.user if request.user.is_authenticated else None, guest_id=self.get_guest_id(request))
        return Response({"message": "تعداد بروزرسانی شد."})

    @action(detail=True, methods=['delete'])
    def remove(self, request: Request, pk=None) -> Response:
        CartService.remove_item(pk, user=request.user if request.user.is_authenticated else None, guest_id=self.get_guest_id(request))
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """User/Guest Orders and Checkout process."""
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    @action(detail=False, methods=['post'])
    def validate_coupon_api(self, request: Request) -> Response:
        code = request.data.get('code')
        if not code:
            return Response({"error": "کد تخفیف وارد نشده است."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            coupon = OrderService.validate_coupon(code)
            return Response({
                "discount_percent": coupon.discount_percent,
                "max_discount_amount": coupon.max_discount_amount
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
                user=request.user if request.user.is_authenticated else None,
                guest_id=request.headers.get('X-Guest-ID'),
                guest_first_name=serializer.validated_data.get('guest_first_name'),
                guest_last_name=serializer.validated_data.get('guest_last_name'),
                guest_phone=serializer.validated_data.get('guest_phone'),
                guest_email=serializer.validated_data.get('guest_email'),
                guest_password=serializer.validated_data.get('guest_password'),
                address_data=address_data,
                shipping_method_id=serializer.validated_data['shipping_method_id'],
                coupon_code=serializer.validated_data.get('coupon_code')
            )
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)