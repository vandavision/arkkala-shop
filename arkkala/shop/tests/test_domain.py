import pytest
from django.core.exceptions import ValidationError
from shop.models import Product, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestDomainRules:
    """Verifies internal business rules enclosed safely within Entity bounds."""

    def test_product_wholesale_validation_enforcement(self) -> None:
        """Tests cross-field validation rules attached to model boundary."""
        product = Product(
            title="Wholesale Bad Product", slug="bad", description="Desc",
            base_price=1000, is_wholesale=True, 
            wholesale_min_quantity=1, wholesale_base_price=1500
        )
        with pytest.raises(ValidationError) as exc:
            product.clean()
        assert "حداقل تعداد" in str(exc.value)
        
        product.wholesale_min_quantity = 5
        with pytest.raises(ValidationError) as exc:
            product.clean()
        assert "کمتر از قیمت پایه" in str(exc.value)

    def test_comment_rating_validation(self, user: User, product: Product) -> None:
        """Proves ratings outside bounds are thrown structurally at full_clean."""
        comment = Comment(product=product, user=user, body="Test", rating=6)
        with pytest.raises(ValidationError):
            comment.full_clean()