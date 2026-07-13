from typing import Dict, Any
from django.db.models import Q, Count, QuerySet
from django.core.cache import cache

from shop.models import Product, Category, Brand


class SearchService:
    """Service class for handling global search and browsing logic."""

    @staticmethod
    def global_search(query: str, limit: int = 5) -> Dict[str, QuerySet]:
        """
        Perform a global search strictly across store items: Products, Brands, and Categories.
        
        Args:
            query (str): The search term.
            limit (int): Maximum number of results per category.
            
        Returns:
            Dict containing querysets for each model.
        """
        if not query:
            return {'products': [], 'brands': [], 'categories': []}

        products = Product.objects.filter(
            Q(title__icontains=query) | Q(english_title__icontains=query),
            is_active=True
        ).prefetch_related('gallery')[:limit]
        
        brands = Brand.objects.filter(
            title__icontains=query, 
            is_active=True
        )[:limit]
        
        categories = Category.objects.filter(
            title__icontains=query, 
            is_active=True
        )[:limit]

        return {
            'products': products,
            'brands': brands,
            'categories': categories
        }

    @staticmethod
    def get_cached_category_tree(request) -> list:
        """
        Fetch the entire Category Tree including top products.
        This operation is heavily cached to guarantee 0ms DB hit times for mega-menus.
        """
        from .serializers import CategoryTreeSerializer
        
        cache_key = "global_category_mega_menu_tree"
        cached_tree = cache.get(cache_key)

        if cached_tree:
            return cached_tree

        # If cache expires, build tree and prefetch active children manually
        categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('children')
        serializer_data = CategoryTreeSerializer(categories, many=True, context={'request': request}).data
        
        # Cache for 2 hours (7200 seconds)
        cache.set(cache_key, serializer_data, timeout=7200)
        return serializer_data

    @staticmethod
    def get_brands_with_product_count() -> QuerySet:
        """
        Fetch all active brands annotated with the number of products they have.
        Ideal for a 'Brands Showcase' page.
        """
        return Brand.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('-product_count')