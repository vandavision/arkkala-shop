from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken

from orders.models.order import Order, OrderRequest
from orders.api.serializers.outputs.order import OrderSerializer, OrderRequestSerializer
from orders.api.serializers.inputs.checkout import CheckoutInputSerializer
from orders.api.serializers.inputs.order_request import OrderRequestInputSerializer

from orders.application.dto.commands import CheckoutCommandDTO, CheckoutAddressDTO, CheckoutGuestDTO, OrderRequestCommandDTO
from orders.domain.exceptions import OrderDomainException
import orders.dependencies as deps
from orders.api.views.base import CustomerIdentifiedMixin
from orders.services.coupon import CouponService

def get_client_ip(request: Request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR') or '127.0.0.1'

class OrderViewSet(CustomerIdentifiedMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

    @action(detail=False, methods=['post'])
    def checkout(self, request: Request) -> Response:
        serializer = CheckoutInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, guest_id = self.get_identity(request)
        client_ip = get_client_ip(request)
        v_data = serializer.validated_data

        address_dto = CheckoutAddressDTO(
            title=v_data.get('title'),
            country=v_data.get('country'),
            province=v_data.get('province'),
            city=v_data.get('city'),
            postal_address=v_data.get('postal_address'),
            postal_code=v_data.get('postal_code'),
            plaque=v_data.get('plaque'),
            building_unit=v_data.get('building_unit')
        )

        guest_dto = CheckoutGuestDTO(
            first_name=v_data.get('guest_first_name'),
            last_name=v_data.get('guest_last_name'),
            phone=v_data.get('guest_phone'),
            email=v_data.get('guest_email'),
            password=v_data.get('guest_password')
        )

        command_dto = CheckoutCommandDTO(
            user_id=user.id if user else None,
            guest_id=guest_id,
            client_ip=client_ip,
            shipping_method_id=str(v_data['shipping_method_id']),
            coupon_code=v_data.get('coupon_code'),
            address=address_dto,
            guest_data=guest_dto
        )

        command = deps.get_checkout_command()

        try:
            order, resolved_user, should_issue_token = command.execute(command_dto)
            response_data = OrderSerializer(order, context={'request': request}).data

            if should_issue_token and resolved_user:
                refresh = RefreshToken.for_user(resolved_user)
                response_data['token'] = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }

            return Response(response_data, status=status.HTTP_201_CREATED)
        except (ValueError, OrderDomainException) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def last_order(self, request: Request) -> Response:
        order = self.get_queryset().order_by('-created_at').first()
        if not order:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order, context={'request': request}).data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def validate_coupon_api(self, request: Request) -> Response:
        code = request.data.get('code')
        if not code:
            return Response({"error": "کد تخفیف ارسال نشده است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = CouponService.validate_coupon(code)
            return Response({
                "code": coupon.code,
                "discount_percent": coupon.discount_percent,
                "max_discount_amount": coupon.max_discount_amount
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderRequestViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderRequestSerializer

    def get_queryset(self):
        return OrderRequest.objects.filter(order__user=self.request.user)

    def create(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        serializer = OrderRequestInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        v_data = serializer.validated_data
        command_dto = OrderRequestCommandDTO(
            user_id=request.user.id,
            order_uuid=str(v_data['order']),
            request_type=v_data['request_type'],
            reason=v_data['reason']
        )

        command = deps.get_order_request_command()

        try:
            order_request = command.execute(command_dto)
            return Response(self.get_serializer(order_request).data, status=status.HTTP_201_CREATED)
        except (ValueError, OrderDomainException) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)