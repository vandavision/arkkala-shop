# shop/services/product.py
from typing import Any, Dict
from django.db.models import F, Max
from django.contrib.auth import get_user_model
from shop.models.product import Product

User = get_user_model()


class ProductService:
    """Business logic for Product entities."""

    @classmethod
    def get_max_price(cls) -> int:
        result = Product.objects.aggregate(max_price=Max('base_price'))
        return int(result.get('max_price') or 0)

    @classmethod
    def increment_view_count(cls, product: Product) -> None:
        Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)
        product.refresh_from_db(fields=['view_count'])

    @classmethod
    def toggle_favorite(cls, product: Product, user: User) -> Dict[str, Any]:
        if product.favorites.filter(id=user.id).exists():
            product.favorites.remove(user)
            return {"is_favorite": False, "message": "کالا از علاقه‌مندی‌های شما حذف شد."}
        
        product.favorites.add(user)
        return {"is_favorite": True, "message": "کالا به لیست علاقه‌مندی‌های شما اضافه شد."}