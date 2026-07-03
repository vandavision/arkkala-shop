"""
Business Logic for Orders and Cart.
"""
from typing import Dict, Any, Optional
from django.db import transaction
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from shop.models import ProductVariant
from .models import Cart, CartItem, Order, OrderItem, OrderStatus, ShippingMethod
from .tasks import cancel_unpaid_order

User = get_user_model()


class CartService:
    """Service to handle Cart operations for Users and Guests."""

    @staticmethod
    def get_or_create_cart(request: HttpRequest) -> Cart:
        """Fetch existing cart or create a new one based on session or user."""
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart
        
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    @staticmethod
    @transaction.atomic
    def merge_guest_cart_to_user(request: HttpRequest) -> None:
        """Called upon login to merge session cart items into user cart."""
        session_key = request.session.session_key
        if not session_key:
            return

        guest_cart = Cart.objects.filter(session_key=session_key).first()
        if not guest_cart:
            return

        user_cart, _ = Cart.objects.get_or_create(user=request.user)
        
        for item in guest_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(cart=user_cart, variant=item.variant)
            if not created:
                user_item.quantity += item.quantity
            else:
                user_item.quantity = item.quantity
            user_item.save()
            
        guest_cart.delete()

    @staticmethod
    def add_item(request: HttpRequest, variant_id: str, quantity: int = 1) -> CartItem:
        """Add item to cart and validate inventory."""
        cart = CartService.get_or_create_cart(request)
        variant = ProductVariant.objects.get(id=variant_id)
        
        if variant.inventory < quantity:
            raise ValueError("موجودی کالا کافی نیست.")

        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        new_quantity = quantity if created else item.quantity + quantity
        
        if new_quantity > variant.inventory:
            raise ValueError("موجودی کالا برای این تعداد درخواست شده کافی نیست.")
            
        item.quantity = new_quantity
        item.save()
        return item


class OrderService:
    """Service to handle Order operations."""

    @staticmethod
    @transaction.atomic
    def checkout(request: HttpRequest, payload: Dict[str, Any]) -> Order:
        """Convert Cart to Order, apply shipping cost, and schedule auto-cancellation."""
        cart = CartService.get_or_create_cart(request)
        items = cart.items.select_related('variant').all()
        
        if not items.exists():
            raise ValueError("سبد خرید شما خالی است.")

        shipping_method_id = payload.get('shipping_method_id')
        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
        except ShippingMethod.DoesNotExist:
            raise ValueError("روش ارسال نامعتبر است.")

        products_total = sum(item.variant.price * item.quantity for item in items)
        shipping_cost = shipping_method.base_cost
        payable_price = products_total + shipping_cost
        
        user = request.user if request.user.is_authenticated else None
        
        order = Order.objects.create(
            user=user,
            guest_mobile=payload.get('guest_mobile'),
            guest_first_name=payload.get('guest_first_name'),
            guest_last_name=payload.get('guest_last_name'),
            shipping_method=shipping_method,
            products_total=products_total,
            shipping_cost=shipping_cost,
            payable_price=payable_price,
            title=payload.get('title'),
            country=payload.get('country', 'Iran'),
            province=payload.get('province'),
            city=payload.get('city'),
            postal_address=payload.get('postal_address'),
            postal_code=payload.get('postal_code'),
            plaque=payload.get('plaque'),
            building_unit=payload.get('building_unit')
        )

        order_items = [
            OrderItem(
                order=order,
                variant=item.variant,
                price=item.variant.price,
                quantity=item.quantity
            ) for item in items
        ]
        OrderItem.objects.bulk_create(order_items)
        
        # Deduct inventory immediately to reserve products
        for item in items:
            item.variant.inventory -= item.quantity
            item.variant.save()

        cart.items.all().delete()

        # Schedule auto-cancel after 1 hour
        cancel_unpaid_order.apply_async((str(order.id),), countdown=3600)

        return order