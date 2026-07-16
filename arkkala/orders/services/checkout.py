from decimal import Decimal
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.db.models import F
from django.conf import settings

from orders.models import Cart, Order, OrderItem, ShippingMethod
from shop.models import Product, ProductVariant
from platform_tools.services.email import EmailService
from orders.tasks import cancel_unpaid_order

from .cart import CartService
from .shipping import PostexShippingService
from .coupon import CouponService
from .customer import CustomerService


class CheckoutService:
    """Facade Service for orchestrating the complete checkout process."""
    
    @staticmethod
    def process_checkout(
        address_data: Dict[str, Any], 
        shipping_method_id: str, 
        guest_data: Dict[str, Any],
        coupon_code: Optional[str] = None, 
        user: Optional[Any] = None, 
        guest_id: Optional[str] = None
    ) -> Order:
        """
        Executes order checkout.
        The external HTTP logic (Postex) executes BEFORE database locking.
        """
        cart: Cart = CartService.get_or_create_cart(user, guest_id)
        cart_items = list(cart.items.select_related('product', 'variant').all())

        if not cart_items:
            raise ValueError("سبد خرید شما خالی است.")

        shipping: ShippingMethod = ShippingMethod.objects.get(pk=shipping_method_id)
        total_items_amount, total_weight = CartService.get_cart_totals(cart_items)

        shipping_cost = Decimal(0) if shipping.is_pay_on_delivery else (
            PostexShippingService.calculate_shipping_cost(
                cart_items, address_data.get('province', 'تهران'), total_weight
            ) + shipping.base_cost
        )

        tax_rate = Decimal(getattr(settings, 'VAT_RATE', 0.10))

        with transaction.atomic():
            cart = Cart.objects.select_for_update().get(pk=cart.pk)
            
            resolved_user = CustomerService.resolve_checkout_user(user, guest_data)
            
            coupon_obj, discount_amount = CouponService.apply_coupon(coupon_code, total_items_amount) if coupon_code else (None, Decimal(0))

            subtotal = total_items_amount - discount_amount
            tax_amount = subtotal * tax_rate
            payable_amount = subtotal + tax_amount + shipping_cost

            order = Order.objects.create(
                user=resolved_user,
                guest_first_name=guest_data.get('guest_first_name'),
                guest_last_name=guest_data.get('guest_last_name'),
                guest_phone=guest_data.get('guest_phone'),
                shipping_method=shipping,
                coupon=coupon_obj,
                total_items_amount=total_items_amount,
                discount_amount=discount_amount,
                shipping_cost=shipping_cost,
                payable_amount=payable_amount,
                **address_data
            )

            CheckoutService._create_items_and_update_inventory(order, cart_items)
            cart.items.all().delete()

        if resolved_user and getattr(resolved_user, 'email', None):
             EmailService.send_order_invoice(order=order, user_email=resolved_user.email)

        cancel_unpaid_order.apply_async((str(order.uuid),), countdown=7200)

        return order

    @staticmethod
    def _create_items_and_update_inventory(order: Order, cart_items: List[Any]) -> None:
        """Helper to cleanly create order items and deduct stock safely."""
        order_items = []
        for item in cart_items:
            unit_price = CartService.calculate_item_price(item)
            order_items.append(
                OrderItem(
                    order=order, product=item.product, variant=item.variant,
                    quantity=item.quantity, unit_price=unit_price, total_price=unit_price * item.quantity
                )
            )

            if item.variant:
                locked_variant = ProductVariant.objects.select_for_update().get(pk=item.variant.pk)
                locked_variant.inventory = F('inventory') - item.quantity
                locked_variant.save(update_fields=['inventory'])
            else:
                locked_product = Product.objects.select_for_update().get(pk=item.product.pk)
                locked_product.base_inventory = F('base_inventory') - item.quantity
                locked_product.save(update_fields=['base_inventory'])
                
        OrderItem.objects.bulk_create(order_items)