import pytest
from typing import Dict, Any
from django.utils import timezone
from datetime import timedelta
from shop.models import (
    Attribute, AttributeValue, Brand, Category, 
    Product, Comment, Question
)

@pytest.mark.django_db
class TestShopModels:
    """
    Unit tests for Shop application models logic and properties.
    """

    def test_attribute_str(self, attribute: Attribute) -> None:
        """
        Validates the string representation of Attribute.
        """
        assert str(attribute) == 'Color'

    def test_attribute_value_str(self, attribute_value: AttributeValue) -> None:
        """
        Validates the string representation of AttributeValue.
        """
        assert str(attribute_value) == 'Color: Red'

    def test_brand_str(self, brand: Brand) -> None:
        """
        Validates the string representation of Brand.
        """
        assert str(brand) == 'Test Brand'

    def test_category_str(self, category: Category) -> None:
        """
        Validates the string representation of Category.
        """
        assert str(category) == 'Test Category'

    def test_product_str(self, product: Product) -> None:
        """
        Validates the string representation of Product.
        """
        assert str(product) == 'Test Product'

    def test_question_str(self, question: Question) -> None:
        """
        Validates the string representation of Question including author resolution.
        """
        assert 'Question on Test Product by Test User' in str(question)

    def test_product_is_special_offer_active(self, product: Product) -> None:
        """
        Validates the special offer dynamic property logic.
        """
        assert product.is_special_offer_active is False
        
        product.special_discount_percent = 10
        product.special_offer_end = timezone.now() + timedelta(days=1)
        product.save()
        
        assert product.is_special_offer_active is True

    def test_product_generate_json_ld(self, product: Product, comment: Comment) -> None:
        """
        Validates the SEO JSON-LD schema generation logic.
        """
        product.average_rating = 5.0
        product.save()

        json_ld: Dict[str, Any] = product.generate_json_ld()
        
        assert "@context" in json_ld
        assert "@graph" in json_ld
        
        product_schema = json_ld["@graph"][0]
        assert product_schema["@type"] == "Product"
        assert product_schema["name"] == "Test Product"
        assert product_schema["offers"]["price"] == "100000"
        assert "aggregateRating" in product_schema
        assert product_schema["aggregateRating"]["ratingValue"] == "5.0"
        assert product_schema["aggregateRating"]["reviewCount"] == "1"