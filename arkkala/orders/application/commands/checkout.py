from decimal import Decimal
from typing import Optional, Tuple
from django.conf import settings
from django.db import transaction

from orders.application.dto.commands import CheckoutCommandDTO
from orders.application.ports.repositories import (
    CartRepository, OrderRepository, CouponRepository, 
    ShippingRepository, InventoryRepository, CustomerRepository
)
from orders.application.ports.shipping import ShippingProvider
from orders.application.ports.event_bus import EventBus
from orders.domain.exceptions import CartEmptyException, InvalidCouponException
from orders.domain.events import OrderCreatedEvent

from orders.services.cart import CartService
from shop.services.interaction import InteractionService

class CheckoutCommand:
    def __init__(
        self, 
        cart_repo: CartRepository, 
        order_repo: OrderRepository,
        coupon_repo: CouponRepository,
        shipping_repo: ShippingRepository,
        inventory_repo: InventoryRepository,
        customer_repo: CustomerRepository,
        shipping_provider: ShippingProvider,
        event_bus: EventBus
    ) -> None:
        self.cart_repo = cart_repo
        self.order_repo = order_repo
        self.coupon_repo = coupon_repo
        self.shipping_repo = shipping_repo
        self.inventory_repo = inventory_repo
        self.customer_repo = customer_repo
        self.shipping_provider = shipping_provider
        self.event_bus = event_bus

    def execute(self, dto: CheckoutCommandDTO) -> Tuple[object, Optional[object], bool]:
        resolved_user, should_issue_token = self.customer_repo.resolve_checkout_user(dto.user_id, dto.guest_data.__dict__)

        with transaction.atomic():
            if resolved_user:
                guest_ids = [g for g in [dto.guest_id, dto.client_ip] if g]
                if guest_ids:
                    InteractionService.merge_guest_history_to_user(resolved_user, guest_ids)
                if dto.guest_id:
                    CartService.merge_guest_cart_to_user_cart(resolved_user, dto.guest_id)

            cart = self.cart_repo.get_or_create_cart(resolved_user.id if resolved_user else None, dto.guest_id)
            cart_items = self.cart_repo.get_cart_items_with_relations(cart)

            if not cart_items:
                raise CartEmptyException("سبد خرید شما خالی است.")

            shipping = self.shipping_repo.get_shipping_method(dto.shipping_method_id)
            if not shipping:
                raise ValueError("روش ارسال نامعتبر است.")

            total_items_amount, total_weight = self.cart_repo.get_cart_totals(cart_items)

            shipping_cost = Decimal(0)
            if not shipping.is_pay_on_delivery:
                provider_cost = self.shipping_provider.calculate_cost(
                    items=cart_items, 
                    dest_province=dto.address.province, 
                    total_weight_grams=total_weight
                )
                shipping_cost = provider_cost + shipping.base_cost

            tax_rate = Decimal(getattr(settings, 'VAT_RATE', 0.10))

            coupon_obj, discount_amount = self._apply_coupon(dto.coupon_code, total_items_amount)

            subtotal = total_items_amount - discount_amount
            tax_amount = subtotal * tax_rate
            payable_amount = subtotal + tax_amount + shipping_cost

            order_data = {
                'user': resolved_user,
                'guest_first_name': dto.guest_data.first_name,
                'guest_last_name': dto.guest_data.last_name,
                'guest_phone': dto.guest_data.phone,
                'shipping_method': shipping,
                'coupon': coupon_obj,
                'total_items_amount': total_items_amount,
                'discount_amount': discount_amount,
                'shipping_cost': shipping_cost,
                'payable_amount': payable_amount,
                **dto.address.__dict__
            }

            order = self.order_repo.create_order(order_data)

            self._create_items_and_deduct_inventory(order, cart_items)
            self.cart_repo.clear_cart(cart)

            event = OrderCreatedEvent(
                order_uuid=str(order.uuid),
                user_email=resolved_user.email if resolved_user and hasattr(resolved_user, 'email') else None
            )
            transaction.on_commit(lambda: self.event_bus.publish(event))

        return order, resolved_user, should_issue_token

    def _apply_coupon(self, coupon_code: Optional[str], total_amount: Decimal) -> Tuple[Optional[object], Decimal]:
        if not coupon_code:
            return None, Decimal(0)

        coupon = self.coupon_repo.get_valid_coupon(coupon_code, lock=True)
        if not coupon:
            raise InvalidCouponException("کد تخفیف نامعتبر است یا ظرفیت آن پر شده است.")

        discount = (total_amount * coupon.discount_percent) / Decimal(100)
        if coupon.max_discount_amount and discount > coupon.max_discount_amount:
            discount = coupon.max_discount_amount

        self.coupon_repo.increment_usage(coupon)
        return coupon, discount

    def _create_items_and_deduct_inventory(self, order: object, cart_items: list) -> None:
        order_items_data = []
        for item in cart_items:
            unit_price = CartService.calculate_item_price(item)
            order_items_data.append({
                'order': order,
                'product': item.product,
                'variant': item.variant,
                'quantity': item.quantity,
                'unit_price': unit_price,
                'total_price': unit_price * item.quantity
            })
            self.inventory_repo.lock_and_deduct_inventory(item.product.pk, item.variant.pk if item.variant else None, item.quantity)

            if getattr(order, 'user', None):
                InteractionService.record_product_purchase(order.user, item.product, 5)

        self.order_repo.create_order_items(order_items_data)