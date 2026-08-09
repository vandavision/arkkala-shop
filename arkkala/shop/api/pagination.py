from rest_framework.pagination import PageNumberPagination

class ProductPagination(PageNumberPagination):
    """Product specific pagination schema."""
    page_size: int = 9
    page_size_query_param: str = 'page_size'
    max_page_size: int = 100