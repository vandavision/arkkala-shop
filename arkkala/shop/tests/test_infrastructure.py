import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from shop.models import Product
import shop.dependencies as deps

@pytest.mark.django_db
class TestInfrastructureAdapters:
    """Validates low level Database Query bounds strictly."""

    def test_optimized_products_query_count(self, product: Product, comment: Any) -> None:
        """Checks if select_related and prefetch decorators correctly limit overhead."""
        query = deps.get_optimized_products_query()
        
        with CaptureQueriesContext(connection) as queries:
            results = list(query.execute(user=None))
            assert len(results) > 0
            
            _ = results[0].brand
            _ = results[0].category
            _ = list(results[0].approved_comments)
            
        assert len(queries) < 6