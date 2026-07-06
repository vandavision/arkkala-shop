"""
API Views for Search, Categories Mega-Menu, and Brands Showcase.
"""
from rest_framework import views, generics, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from .services import SearchService
from .serializers import (
    GlobalSearchResponseSerializer,
    CategoryTreeSerializer,
    BrandBrowseSerializer
)


class GlobalSearchView(views.APIView):
    """
    API endpoint for the main search bar (Autocomplete).
    Searches across products, posts, brands, and categories simultaneously.
    """
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 5))
        
        results = SearchService.global_search(query, limit)
        
        serializer = GlobalSearchResponseSerializer(results, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryTreeView(generics.ListAPIView):
    """
    API endpoint to retrieve the entire active category tree.
    Perfect for building Frontend Mega-Menus.
    """
    permission_classes = [AllowAny]
    serializer_class = CategoryTreeSerializer
    pagination_class = None

    def get_queryset(self):
        return SearchService.get_category_tree()


class BrandBrowseView(generics.ListAPIView):
    """
    API endpoint to retrieve all active brands with their product counts.
    Perfect for the 'Brands' page.
    """
    permission_classes = [AllowAny]
    serializer_class = BrandBrowseSerializer

    def get_queryset(self):
        return SearchService.get_brands_with_product_count()