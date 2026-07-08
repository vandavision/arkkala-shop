"""
Service Layer for Orders and Cart processing.
"""
import re
import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional

import requests
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Cart, CartItem, Order, OrderItem, ShippingMethod, Coupon
from shop.models import Product, ProductVariant
from platform_tools.services.email import EmailService
from .tasks import cancel_unpaid_order

User = get_user_model()
logger = logging.getLogger(__name__)


class ExternalShippingAPI:
    @staticmethod
    def calculate_post_cost(total_weight_grams: int, origin_province: str, dest_province: str) -> Decimal:
        base_post_cost: int = 35000
        weight_penalty: int = (total_weight_grams // 500) * 5000
        distance_multiplier: float = 1.0 if origin_province == dest_province else 1.35
        final_cost: float = (base_post_cost + weight_penalty) * distance_multiplier
        return Decimal(int(final_cost))


class PostexShippingService:
    BASE_URL: str = getattr(settings, 'POSTEX_BASE_URL', 'https://api.postex.ir')
    API_KEY: str = getattr(settings, 'POSTEX_API_KEY', '')
    FROM_CITY_CODE: int = getattr(settings, 'POSTEX_FROM_CITY_CODE', 1)

    @classmethod
    def calculate_shipping_cost(cls, cart_items: List[CartItem], dest_province: str, total_weight_grams: int) -> Decimal:
        parcels_payload: List[Dict[str, Any]] = []

        for item in cart_items:
            item_weight: int = CartService.calculate_item_weight(item)
            quantity: int = item.quantity
            volume: int = getattr(item.product, 'volume', 1000)
            side_dimension: int = int(volume ** (1/3)) or 10

            parcels_payload.append({
                "length": side_dimension,
                "width": side_dimension,
                "height": side_dimension,
                "total_weight": item_weight * quantity,
                "is_fragile": getattr(item.product, 'is_fragile', False),
                "is_liquid": getattr(item.product, 'is_liquid', False),
                "total_value": float(CartService.calculate_item_price(item) * quantity),
                "pre_paid_amount": 0,
                "total_value_currency": "IRR",
                "box_type_id": 0
            })

        payload: Dict[str, Any] = {
            "collection_type": "pick_up",
            "from_city_code": cls.FROM_CITY_CODE,
            "courier": {
                "courier_code": "post",
                "service_type": "pishtaz"
            },
            "parcels": parcels_payload,
            "value_added_service": {
                "request_label": False,
                "request_packaging": False,
                "request_sms_notification": True
            }
        }

        headers: Dict[str, str] = {
            "x-api-key": cls.API_KEY,
            "Content-Type": "application/json"
        }

        try:
            if not cls.API_KEY:
                raise ValueError("API Key is not configured.")

            response = requests.post(
                f"{cls.BASE_URL}/api/v1/shipping/quotes",
                json=payload,
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                data: Any = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return Decimal(int(data[0].get('price', 0) or data[0].get('cost', 0)))
                elif isinstance(data, dict):
                    return Decimal(int(data.get('amount', 0) or data.get('total_amount', 0)))

                raise ValueError("فرمت پاسخ جی‌سان پستکس معتبر نیست.")
            else:
                response.raise_for_status()

        except Exception as e:
            logger.error(f"Postex API Error: {str(e)}. Falling back to algorithmic calculation.")
            return ExternalShippingAPI.calculate_post_cost(
                total_weight_grams=total_weight_grams,
                origin_province="تهران",
                dest_province=dest_province
            )


class CartService:
    @staticmethod
    def get_or_create_cart(user: Optional[User] = None, guest_id: Optional[str] = None) -> Cart:
        if user and user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            if guest_id:
                guest_cart = Cart.objects.filter(guest_id=guest_id, user__isnull=True).first()
                if guest_cart:
                    for item in guest_cart.items.all():
                        item.cart = cart
                        item.save()
                    guest_cart.delete()
            return cart
        elif guest_id:
            cart, _ = Cart.objects.get_or_create(guest_id=guest_id, user__isnull=True)
            return cart
        else:
            raise ValueError("باید شناسه کاربر یا مهمان موجود باشد.")

    @staticmethod
    def add_to_cart(product_id: str, variant_id: Optional[str] = None, quantity: int = 1, user: Optional[User] = None, guest_id: Optional[str] = None) -> CartItem:
        cart: Cart = CartService.get_or_create_cart(user, guest_id)
        item: Optional[CartItem] = CartItem.objects.filter(cart=cart, product_id=product_id, variant_id=variant_id).first()

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
    def update_item_quantity(item_id: str, quantity: int, user: Optional[User] = None, guest_id: Optional[str] = None) -> CartItem:
        cart: Cart = CartService.get_or_create_cart(user, guest_id)
        item: CartItem = CartItem.objects.get(pk=item_id, cart=cart)
        item.quantity = quantity
        item.save(update_fields=['quantity'])
        return item

    @staticmethod
    def remove_item(item_id: str, user: Optional[User] = None, guest_id: Optional[str] = None) -> None:
        cart: Cart = CartService.get_or_create_cart(user, guest_id)
        CartItem.objects.filter(pk=item_id, cart=cart).delete()

    @staticmethod
    def calculate_item_price(item: CartItem) -> Decimal:
        product: Product = item.product
        variant: Optional[ProductVariant] = item.variant
        qty: int = item.quantity

        final_price = variant.price if variant else product.base_price

        if product.is_wholesale and qty >= product.wholesale_min_quantity:
            if variant and variant.wholesale_price:
                final_price = variant.wholesale_price
            elif not variant and product.wholesale_base_price:
                final_price = product.wholesale_base_price

        if getattr(product, 'is_special_offer_active', False):
            discount_multiplier = Decimal(1 - (product.special_discount_percent / 100))
            special_price = (variant.price if variant else product.base_price) * discount_multiplier
            
            if special_price < final_price:
                final_price = special_price

        return Decimal(int(final_price))

    @staticmethod
    def calculate_item_weight(item: CartItem) -> int:
        product: Product = item.product
        variant: Optional[ProductVariant] = item.variant
        weight: int = getattr(product, 'weight', 500)

        if variant:
            for attr_val in variant.attribute_values.all():
                title: str = attr_val.attribute.title.lower()
                val_text: str = attr_val.value.lower()

                if 'وزن' in title or 'weight' in title or 'سایز' in title or 'size' in title:
                    numbers: List[str] = re.findall(r'\d+', val_text)
                    if numbers:
                        extracted_val: int = int(numbers[0])
                        if 'کیلو' in val_text or 'kg' in val_text or extracted_val < 20:
                            weight = extracted_val * 1000
                        else:
                            weight = extracted_val
                        break

        return weight


class OrderService:
    @staticmethod
    def validate_coupon(code: str) -> Coupon:
        now = timezone.now()
        coupon: Optional[Coupon] = Coupon.objects.filter(
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
    def checkout(
        address_data: Dict[str, Any], 
        shipping_method_id: str, 
        coupon_code: Optional[str] = None, 
        user: Optional[User] = None, 
        guest_id: Optional[str] = None, 
        guest_phone: Optional[str] = None, 
        guest_first_name: Optional[str] = None, 
        guest_last_name: Optional[str] = None,
        guest_email: Optional[str] = None,
        guest_password: Optional[str] = None 
    ) -> Order:
        
        cart: Cart = CartService.get_or_create_cart(user, guest_id)
        cart_items = cart.items.select_related('product', 'variant').all()

        if not cart_items.exists():
            raise ValueError("سبد خرید شما خالی است.")


        if not user:
            if guest_email and guest_password:
                user, created = User.objects.get_or_create(
                    email=guest_email,
                    defaults={
                        'username': guest_email,
                        'first_name': guest_first_name or '',
                        'last_name': guest_last_name or '',
                        'is_active': True
                    }
                )
                if created:
                    user.set_password(guest_password)
                    user.save()
            elif guest_phone:
                user, created = User.objects.get_or_create(
                    phone_number=guest_phone,
                    defaults={
                        'username': guest_phone,
                        'first_name': guest_first_name or '',
                        'last_name': guest_last_name or '',
                        'is_active': True
                    }
                )
        
        # Update names if they were missing for existing users
        if user:
            update_fields = []
            if not user.first_name and guest_first_name:
                user.first_name = guest_first_name
                update_fields.append('first_name')
            if not user.last_name and guest_last_name:
                user.last_name = guest_last_name
                update_fields.append('last_name')
            if not user.phone_number and guest_phone:
                user.phone_number = guest_phone
                update_fields.append('phone_number')
            
            if update_fields:
                user.save(update_fields=update_fields)

        shipping: ShippingMethod = ShippingMethod.objects.get(pk=shipping_method_id)

        total_items_amount: Decimal = Decimal(0)
        total_weight_grams: int = 0

        for item in cart_items:
            unit_price: Decimal = CartService.calculate_item_price(item)
            total_items_amount += unit_price * item.quantity
            item_weight: int = CartService.calculate_item_weight(item)
            total_weight_grams += item_weight * item.quantity

        if shipping.is_pay_on_delivery:
            shipping_cost: Decimal = Decimal(0)
        else:
            calculated_api_cost: Decimal = PostexShippingService.calculate_shipping_cost(
                cart_items=list(cart_items),
                dest_province=address_data.get('province', 'تهران'),
                total_weight_grams=total_weight_grams
            )
            shipping_cost = calculated_api_cost + shipping.base_cost

        discount_amount: Decimal = Decimal(0)
        coupon: Optional[Coupon] = None

        if coupon_code:
            coupon = OrderService.validate_coupon(coupon_code)
            discount_amount = (total_items_amount * coupon.discount_percent) / Decimal(100)
            if coupon.max_discount_amount and discount_amount > coupon.max_discount_amount:
                discount_amount = coupon.max_discount_amount

            coupon.used_count = F('used_count') + 1
            coupon.save(update_fields=['used_count'])

        tax_rate: Decimal = Decimal(getattr(settings, 'VAT_RATE', 0.10))
        subtotal: Decimal = (total_items_amount - discount_amount)
        tax_amount: Decimal = subtotal * tax_rate

        payable_amount: Decimal = subtotal + tax_amount + shipping_cost

        order: Order = Order.objects.create(
            user=user,
            guest_first_name=guest_first_name,
            guest_last_name=guest_last_name,
            guest_phone=guest_phone,
            shipping_method=shipping,
            coupon=coupon,
            total_items_amount=total_items_amount,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            payable_amount=payable_amount,
            **address_data
        )

        order_items_to_create: List[OrderItem] = []

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

        if user and user.is_authenticated and getattr(user, 'email', None):
             EmailService.send_order_invoice(order=order, user_email=user.email)

        cancel_unpaid_order.apply_async((str(order.uuid),), countdown=7200)

        return order