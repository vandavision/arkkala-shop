from typing import Optional, List, Tuple
from decimal import Decimal
from orders.models.cart import Cart, CartItem
from orders.application.ports.repositories import CartRepository
from orders.services.cart import CartService

class DjangoCartRepository(CartRepository):
    """
    Django ORM implementation of CartRepository mapping directly to application layer interfaces.
    """
    def get_or_create_cart(self, user_id: Optional[int], guest_id: Optional[str]) -> Cart:
        if user_id:
            cart, _ = Cart.objects.get_or_create(user_id=user_id)
            return cart
            
        if guest_id:
            cart, _ = Cart.objects.get_or_create(guest_id=guest_id, user__isnull=True)
            return cart
            
        raise ValueError("باید شناسه کاربر یا مهمان موجود باشد.")

    def get_cart_items_with_relations(self, cart: Cart) -> List[CartItem]:
        return list(cart.items.select_related('product', 'variant').all())

    def get_cart_totals(self, cart_items: List[CartItem]) -> Tuple[Decimal, int]:
        return CartService.get_cart_totals(cart_items)

    def clear_cart(self, cart: Cart) -> None:
        cart.items.all().delete()