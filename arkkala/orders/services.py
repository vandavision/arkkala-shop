"""
Service Layer for Orders and Cart processing.
"""
from decimal import Decimal
from typing import Tuple, Dict, Any

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Cart, CartItem, Order, OrderItem, ShippingMethod, Coupon
from shop.models import Product, ProductVariant
from platform_tools.services.email import EmailService

User = get_user_model()


class CartService:
    """Business logic for Cart management."""
    
    @staticmethod
    def get_user_cart(user: User) -> Cart:
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_to_cart(user: User, product_id: str, variant_id: str = None, quantity: int = 1) -> CartItem:
        cart = CartService.get_user_cart(user)
        
        item = CartItem.objects.filter(cart=cart, product_id=product_id, variant_id=variant_id).first()
        if item:
            item.quantity += quantity
            item.save(update_fields=['quantity'])
        else:
            item = CartItem.objects.create(
                cart=cart,
                product_id=product_id,
                variant_id=variant_id,
                quantity=quantity
            )
        return item

    @staticmethod
    def update_item_quantity(item_id: str, user: User, quantity: int) -> CartItem:
        item = CartItem.objects.get(id=item_id, cart__user=user)
        item.quantity = quantity
        item.save(update_fields=['quantity'])
        return item

    @staticmethod
    def remove_item(item_id: str, user: User) -> None:
        CartItem.objects.filter(id=item_id, cart__user=user).delete()

    @staticmethod
    def calculate_item_price(item: CartItem) -> Decimal:
        """
        محاسبه هوشمند قیمت. اگر تعداد خرید کاربر به حدنصاب عمده برسد و فروش عمده فعال باشد،
        قیمت به صورت عمده شکسته می‌شود.
        """
        product = item.product
        variant = item.variant
        qty = item.quantity
        
        if variant:
            if product.is_wholesale and qty >= product.wholesale_min_quantity and variant.wholesale_price:
                return variant.wholesale_price
            return variant.price
        else:
            if product.is_wholesale and qty >= product.wholesale_min_quantity and product.wholesale_base_price:
                return product.wholesale_base_price
            return product.base_price


class OrderService:
    """Business logic for Checkout and Orders."""
    
    @staticmethod
    def validate_coupon(code: str) -> Coupon:
        """Check if coupon is active, within date range, and under usage limits."""
        now = timezone.now()
        coupon = Coupon.objects.filter(
            code__iexact=code,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
            used_count__lt=F('usage_limit')
        ).first()
        
        if not coupon:
            raise ValueError("کد تخفیف نامعتبر است یا منقضی شده است.")
        return coupon

    @staticmethod
    @transaction.atomic
    def checkout(user: User, address_data: Dict[str, Any], shipping_method_id: str, coupon_code: str = None) -> Order:
        """
        Convert cart to a finalized Order.
        Calculates shipping cost based on is_pay_on_delivery logic.
        """
        cart = CartService.get_user_cart(user)
        cart_items = cart.items.select_related('product', 'variant').all()
        
        if not cart_items.exists():
            raise ValueError("سبد خرید شما خالی است.")
            
        shipping = ShippingMethod.objects.get(id=shipping_method_id)
        
        total_items_amount = Decimal(0)
        for item in cart_items:
            unit_price = CartService.calculate_item_price(item)
            total_items_amount += unit_price * item.quantity

        shipping_cost = Decimal(0) if shipping.is_pay_on_delivery else shipping.base_cost
        
        discount_amount = Decimal(0)
        coupon = None
        if coupon_code:
            coupon = OrderService.validate_coupon(coupon_code)
            discount_amount = (total_items_amount * coupon.discount_percent) / Decimal(100)
            if coupon.max_discount_amount and discount_amount > coupon.max_discount_amount:
                discount_amount = coupon.max_discount_amount
            
            coupon.used_count = F('used_count') + 1
            coupon.save(update_fields=['used_count'])
            
        tax_rate = Decimal(getattr(settings, 'VAT_RATE', 0.10))
        subtotal = (total_items_amount - discount_amount)
        tax_amount = subtotal * tax_rate
            
        payable_amount = subtotal + tax_amount + shipping_cost
        
        order = Order.objects.create(
            user=user,
            shipping_method=shipping,
            coupon=coupon,
            total_items_amount=total_items_amount,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            payable_amount=payable_amount,
            **address_data
        )
        
        order_items_to_create = []
        for item in cart_items:
            unit_price = CartService.calculate_item_price(item)
            order_items_to_create.append(
                OrderItem(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    total_price=unit_price * item.quantity
                )
            )
            if item.variant:
                item.variant.inventory = F('inventory') - item.quantity
                item.variant.save(update_fields=['inventory'])
            else:
                item.product.base_inventory = F('base_inventory') - item.quantity
                item.product.save(update_fields=['base_inventory'])
                
        OrderItem.objects.bulk_create(order_items_to_create)
        
        cart_items.delete()
        
        if user.email:
             EmailService.send_order_invoice(order=order, user_email=user.email)
        
        return order