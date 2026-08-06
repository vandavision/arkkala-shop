from typing import Optional, Any
from django.db.models import F
from shop.models.product import Product
from shop.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    """
    Handles optimized database transactions and data abstraction for Products.
    """
    def __init__(self) -> None:
        super().__init__(Product)

    def increment_view_count(self, slug: str) -> bool:
        """
        Atomically increments the view count to prevent Lost Update race conditions.
        """
        updated_count = self.model.objects.filter(slug=slug).update(view_count=F('view_count') + 1)
        return updated_count > 0

    def toggle_favorite(self, product_slug: str, user_id: Any) -> Optional[bool]:
        """
        Optimized toggling without loading massive related datasets.
        Returns True if added, False if removed.
        """
        product = self.get_by_slug(product_slug)
        if not product:
            raise ValueError("Product not found.")

        is_favorited: bool = product.favorites.filter(id=user_id).exists()
        if is_favorited:
            product.favorites.remove(user_id)
            return False
        
        product.favorites.add(user_id)
        return True