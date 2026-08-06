import pytest
from typing import Dict, Any
from django.utils import timezone
from datetime import timedelta
from shop.models import Attribute, AttributeValue, Brand, Category, Product, Comment, Question
from shop.filters import ProductFilter

@pytest.mark.django_db
class TestShopModels:

    def test_attribute_str(self, attribute: Attribute) -> None:
        assert str(attribute) == 'Color'

    def test_attribute_value_str(self, attribute_value: AttributeValue) -> None:
        assert str(attribute_value) == 'Color: Red'

    def test_brand_str(self, brand: Brand) -> None:
        assert str(brand) == 'Test Brand'

    def test_category_str(self, category: Category) -> None:
        assert str(category) == 'Test Category'

    def test_product_str(self, product: Product) -> None:
        assert str(product) == 'Test Product'

    def test_question_str(self, question: Question) -> None:
        assert 'Question on Test Product by Test User' in str(question)

    def test_product_is_special_offer_active(self, product: Product) -> None:
        assert product.is_special_offer_active is False
        
        product.special_discount_percent = 10
        product.special_offer_end = timezone.now() + timedelta(days=1)
        product.save()
        assert product.is_special_offer_active is True

    def test_product_generate_json_ld(self, product: Product, comment: Comment) -> None:
        product.average_rating = 5.0
        product.save()
        json_ld: Dict[str, Any] = product.generate_json_ld()
        assert "@context" in json_ld
        
    def test_product_manager_unauthenticated(self, product: Product) -> None:
        qs = Product.objects.with_user_favorite(None)
        assert qs.count() > 0


@pytest.mark.django_db
class TestProductFilters:

    def test_filter_brands(self, product: Product) -> None:
        qs = Product.objects.all()
        f = ProductFilter(data={'brands': product.brand.slug}, queryset=qs)
        assert f.qs.count() == 1
        
        f_empty = ProductFilter(data={'brands': ''}, queryset=qs)
        assert f_empty.qs.count() == 1

    def test_filter_min_max_price(self, product: Product) -> None:
        qs = Product.objects.all()
        f_min = ProductFilter(data={'min_price': 100}, queryset=qs)
        assert f_min.qs.count() == 1
        
        f_max = ProductFilter(data={'max_price': 999999}, queryset=qs)
        assert f_max.qs.count() == 1

    def test_filter_search(self, product: Product) -> None:
        qs = Product.objects.all()
        f = ProductFilter(data={'search': 'Test'}, queryset=qs)
        assert f.qs.count() == 1
        
        f_empty = ProductFilter(data={'search': ''}, queryset=qs)
        assert f_empty.qs.count() == 1

    def test_filter_booleans(self, product: Product) -> None:
        qs = Product.objects.all()
        
        # has_discount
        f_disc = ProductFilter(data={'has_discount': True}, queryset=qs)
        assert f_disc.qs.count() == 0 
        
        # is_special_offer
        f_spec = ProductFilter(data={'is_special_offer': True}, queryset=qs)
        assert f_spec.qs.count() == 0

        # has_stock
        f_stock = ProductFilter(data={'has_stock': True}, queryset=qs)
        assert f_stock.qs.count() == 1
        
        f_no_stock = ProductFilter(data={'has_stock': False}, queryset=qs)
        assert f_no_stock.qs.count() == 0