from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from orders.models import Order, OrderRequest
from orders.serializers.order import OrderSerializer, OrderRequestSerializer
from orders.serializers.checkout import CheckoutSerializer
from orders.services.checkout import CheckoutService
from orders.services.coupon import CouponService
from orders.services.order import OrderRequestService
from .base import CustomerIdentifiedMixin


class OrderViewSet(CustomerIdentifiedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """User/Guest Orders Router."""
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    @action(detail=False, methods=['post'])
    def validate_coupon_api(self, request: Request) -> Response:
        try:
            coupon = CouponService.validate_coupon(request.data.get('code'))
            return Response({
                "discount_percent": coupon.discount_percent, 
                "max_discount_amount": coupon.max_discount_amount
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def checkout(self, request: Request) -> Response:
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user, guest_id = self.get_identity(request)
        v_data = serializer.validated_data
        
        address_data = {
            'title': v_data.get('title'),
            'country': v_data.get('country'),
            'province': v_data.get('province'),
            'city': v_data.get('city'),
            'postal_address': v_data.get('postal_address'),
            'postal_code': v_data.get('postal_code'),
            'plaque': v_data.get('plaque'),
            'building_unit': v_data.get('building_unit')
        }
        
        guest_data = {
            'guest_first_name': v_data.get('guest_first_name'),
            'guest_last_name': v_data.get('guest_last_name'),
            'guest_phone': v_data.get('guest_phone'),
            'guest_email': v_data.get('guest_email'),
            'guest_password': v_data.get('guest_password')
        }
        
        try:
            order = CheckoutService.process_checkout(
                address_data=address_data,
                shipping_method_id=v_data['shipping_method_id'],
                guest_data=guest_data,
                coupon_code=v_data.get('coupon_code'),
                user=user, 
                guest_id=guest_id
            )
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderRequestViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Handles User Return/Cancel Requests."""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderRequestSerializer

    def get_queryset(self):
        return OrderRequest.objects.filter(order__user=self.request.user)

    def create(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        try:
            order_request = OrderRequestService.create_request(
                user=request.user, 
                order_id=request.data.get('order'), 
                request_type=request.data.get('request_type'),
                reason=request.data.get('reason')
            )
            return Response(self.get_serializer(order_request).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)