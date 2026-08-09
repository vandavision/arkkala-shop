from typing import Optional, Any
from django.db.models import F, Max, QuerySet
from shop.models.product import Product, ProductFavorite
from shop.application.ports.repositories import ProductRepositoryPort

class DjangoProductRepository(ProductRepositoryPort):
    """Django ORM Implementation of Product Repository Port."""

    def get_by_slug(self, slug: str) -> Optional[Product]:
        """Resolves the entity via slug."""
        return Product.objects.filter(slug=slug).first()

    def increment_view_count(self, slug: str) -> bool:
        """Executes a thread-safe atomic counter increment."""
        updated = Product.objects.filter(slug=slug).update(view_count=F('view_count') + 1)
        return updated > 0

    def toggle_favorite(self, product_slug: str, user_id: Any) -> bool:
        """Modifies Explicit M2M relationship avoiding full instantiation."""
        product_id = Product.objects.filter(slug=product_slug).values_list('uuid', flat=True).first()
        
        if not product_id:
            raise ValueError("Product not found")

        deleted_count, _ = ProductFavorite.objects.filter(product_id=product_id, user_id=user_id).delete()
        
        if deleted_count > 0:
            return False
            
        ProductFavorite.objects.create(product_id=product_id, user_id=user_id)
        return True

    def get_max_base_price(self) -> int:
        """Performs raw DB aggregation."""
        result = Product.objects.filter(is_active=True).aggregate(max_price=Max('base_price'))
        return int(result.get('max_price') or 0)

    def get_active_products_optimized(self, user: Any) -> QuerySet:
        """Utilizes deep ORM optimizers for API reading."""
        qs = Product.objects.active().with_relations().with_approved_feedback()
        return qs.with_user_favorite(user)
        
    def save_product(self, product: Product) -> Product:
        """Persists a new or updated product instance."""
        product.save()
        return product