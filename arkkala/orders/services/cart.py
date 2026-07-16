import re
from decimal import Decimal
from typing import List, Optional, Tuple, Iterable
from django.contrib.auth.models import AbstractUser

from orders.models import Cart, CartItem
from shop.models import Product, ProductVariant


class CartService:
    """Business logic for Cart management and price calculations."""
    
    @staticmethod
    def get_or_create_cart(user: Optional[AbstractUser] = None, guest_id: Optional[str] = None) -> Cart:
        """Retrieves cart safely for both users and guests, merging if needed."""
        if user and user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=user)
            if guest_id:
                guest_cart = Cart.objects.filter(guest_id=guest_id, user__isnull=True).first()
                if guest_cart:
                    guest_cart.items.all().update(cart=cart)
                    guest_cart.delete()
            return cart
            
        if guest_id:
            cart, _ = Cart.objects.get_or_create(guest_id=guest_id, user__isnull=True)
            return cart
            
        raise ValueError("باید شناسه کاربر یا مهمان موجود باشد.")

    @staticmethod
    def add_to_cart(product_id: str, variant_id: Optional[str] = None, quantity: int = 1, 
                    user: Optional[AbstractUser] = None, guest_id: Optional[str] = None) -> CartItem:
        cart = CartService.get_or_create_cart(user, guest_id)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id, variant_id=variant_id,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=['quantity'])
        return item

    @staticmethod
    def update_item_quantity(item_id: str, quantity: int, user: Optional[AbstractUser] = None, guest_id: Optional[str] = None) -> CartItem:
        cart = CartService.get_or_create_cart(user, guest_id)
        item = CartItem.objects.get(pk=item_id, cart=cart)
        item.quantity = quantity
        item.save(update_fields=['quantity'])
        return item

    @staticmethod
    def remove_item(item_id: str, user: Optional[AbstractUser] = None, guest_id: Optional[str] = None) -> None:
        cart = CartService.get_or_create_cart(user, guest_id)
        CartItem.objects.filter(pk=item_id, cart=cart).delete()

    @staticmethod
    def get_cart_totals(cart_items: Iterable[CartItem]) -> Tuple[Decimal, int]:
        """Calculates total price and total weight for a list of items (DRY Optimization)."""
        total_amount = Decimal(0)
        total_weight = 0
        for item in cart_items:
            total_amount += CartService.calculate_item_price(item) * item.quantity
            total_weight += CartService.calculate_item_weight(item) * item.quantity
        return total_amount, total_weight

    @staticmethod
    def calculate_item_price(item: CartItem) -> Decimal:
        product: Product = item.product
        variant: Optional[ProductVariant] = item.variant
        
        final_price = variant.price if variant else product.base_price

        if product.is_wholesale and item.quantity >= product.wholesale_min_quantity:
            wholesale_price = variant.wholesale_price if variant else product.wholesale_base_price
            if wholesale_price:
                final_price = wholesale_price

        if getattr(product, 'is_special_offer_active', False):
            discount_multiplier = Decimal(1 - (product.special_discount_percent / 100))
            special_price = (variant.price if variant else product.base_price) * discount_multiplier
            final_price = min(final_price, special_price)

        return Decimal(int(final_price))

    @staticmethod
    def calculate_item_weight(item: CartItem) -> int:
        product: Product = item.product
        variant: Optional[ProductVariant] = item.variant
        weight: int = getattr(product, 'weight', 500)

        if variant:
            for attr_val in variant.attribute_values.all():
                title, val_text = attr_val.attribute.title.lower(), attr_val.value.lower()
                if any(k in title for k in ('وزن', 'weight', 'سایز', 'size')):
                    numbers: List[str] = re.findall(r'\d+', val_text)
                    if numbers:
                        extracted_val = int(numbers[0])
                        weight = extracted_val * 1000 if ('کیلو' in val_text or 'kg' in val_text or extracted_val < 20) else extracted_val
                        break
        return weight