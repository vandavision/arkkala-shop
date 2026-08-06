import pytest
import uuid
from shop.repositories.product import ProductRepository
from shop.models import Product

@pytest.mark.django_db
class TestProductRepository:
    def test_base_repository_not_found(self):
        repo = ProductRepository()
        assert repo.get_by_uuid(uuid.uuid4()) is None
        assert repo.get_by_slug("non-existent-slug") is None

    def test_base_repository_save_and_delete(self, product):
        repo = ProductRepository()
        product.title = "Updated Title"
        repo.save(product)
        
        product_from_db = repo.get_by_uuid(product.uuid)
        assert product_from_db.title == "Updated Title"
        
        repo.delete(product_from_db)
        assert repo.get_by_uuid(product.uuid) is None

    def test_toggle_favorite_not_found(self):
        repo = ProductRepository()
        with pytest.raises(ValueError, match="Product not found."):
            repo.toggle_favorite("non-existent-slug", 1)