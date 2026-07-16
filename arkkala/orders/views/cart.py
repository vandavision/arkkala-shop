from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from shop.models import Comment, Question
from orders.serializers.cart import CartItemSerializer
from orders.services.cart import CartService
from .base import CustomerIdentifiedMixin


class CartViewSet(CustomerIdentifiedMixin, viewsets.ViewSet):
    """Manage User & Guest Cart securely."""
    permission_classes = [AllowAny]

    def list(self, request: Request) -> Response:
        user, guest_id = self.get_identity(request)
        if not user and not guest_id:
            return Response([])

        cart = CartService.get_or_create_cart(user, guest_id)
        items = cart.items.select_related('product', 'product__brand', 'product__category', 'variant').prefetch_related(
            'variant__attribute_values', 'product__variants__attribute_values',
            'product__gallery', 'product__videos', 'product__price_history',
            Prefetch('product__comments', queryset=Comment.objects.filter(is_approved=True), to_attr='approved_comments'),
            Prefetch('product__questions', queryset=Question.objects.filter(is_approved=True), to_attr='approved_questions')
        ).all()

        return Response(CartItemSerializer(items, many=True, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    def add(self, request: Request) -> Response:
        user, guest_id = self.get_identity(request)
        if not user and not guest_id:
            return Response({"error": "شناسه دستگاه مشخص نیست."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        CartService.add_to_cart(
            product_id=serializer.validated_data['product'].pk,
            variant_id=serializer.validated_data.get('variant').pk if serializer.validated_data.get('variant') else None,
            quantity=serializer.validated_data.get('quantity', 1),
            user=user, guest_id=guest_id
        )
        return Response({"message": "اضافه شد."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request: Request, pk=None) -> Response:
        user, guest_id = self.get_identity(request)
        CartService.update_item_quantity(pk, int(request.data.get('quantity')), user, guest_id)
        return Response({"message": "بروزرسانی شد."})

    @action(detail=True, methods=['delete'])
    def remove(self, request: Request, pk=None) -> Response:
        user, guest_id = self.get_identity(request)
        CartService.remove_item(pk, user, guest_id)
        return Response(status=status.HTTP_204_NO_CONTENT)