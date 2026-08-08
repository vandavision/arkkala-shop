from rest_framework.pagination import PageNumberPagination

class BlogPagination(PageNumberPagination):
    page_size: int = 9
    page_size_query_param: str = 'page_size'
    max_page_size: int = 100