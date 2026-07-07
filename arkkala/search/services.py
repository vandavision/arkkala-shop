"""
Service Layer for Search App.
Handles global searching and aggregation for categories and brands.
"""
from typing import Dict, Any
from django.db.models import Q, Count, QuerySet

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
        )[:limit]
        
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
    def get_category_tree() -> QuerySet:
        """
        Fetch all active parent categories with their children nested.
        Ideal for Mega-Menus.
        """
        return Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('children')

    @staticmethod
    def get_brands_with_product_count() -> QuerySet:
        """
        Fetch all active brands annotated with the number of products they have.
        Ideal for a 'Brands Showcase' page.
        """
        return Brand.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_property('-product_count') if hasattr(Brand.objects, 'order_property') else \
               Brand.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('-product_count')