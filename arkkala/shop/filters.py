"""
Custom filters for Shop API.
"""
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="base_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="base_price", lookup_expr='lte')
    has_stock = filters.BooleanFilter(method='filter_has_stock')
    has_discount = filters.BooleanFilter(method='filter_has_discount')
    brands = filters.CharFilter(method='filter_brands')
    colors = filters.CharFilter(method='filter_colors')

    class Meta:
        model = Product
        fields = ['category__slug', 'brand__slug', 'is_variable', 'is_wholesale']

    def filter_has_stock(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(base_inventory__gt=0) | Q(variants__inventory__gt=0)
            ).distinct()
        elif value is False:
            return queryset.filter(base_inventory=0, variants__isnull=True).distinct()
        return queryset

    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(wholesale_base_price__isnull=False).distinct()
        return queryset

    def filter_brands(self, queryset, name, value):
        if value:
            brand_slugs = [slug.strip() for slug in value.split(',') if slug.strip()]
            return queryset.filter(brand__slug__in=brand_slugs).distinct()
        return queryset

    def filter_colors(self, queryset, name, value):
        if value:
            color_names = [color.strip() for color in value.split(',') if color.strip()]
            return queryset.filter(variants__attribute_values__value__in=color_names).distinct()
        return queryset