"""
Filters for Shop App.
"""
import django_filters
from django.db.models import Q
from django.utils import timezone
from .models import Product

class ProductFilter(django_filters.FilterSet):
    category__slug = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    brands = django_filters.CharFilter(method='filter_brands')
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    search = django_filters.CharFilter(method='filter_search')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')
    is_special_offer = django_filters.BooleanFilter(method='filter_is_special_offer')
    has_stock = django_filters.BooleanFilter(method='filter_has_stock')

    class Meta:
        model = Product
        fields = [
            'category__slug', 'brands', 'min_price', 'max_price', 
            'search', 'has_discount', 'is_special_offer', 'has_stock'
        ]

    def filter_brands(self, queryset, name, value):
        if value:
            brands = value.split(',')
            return queryset.filter(brand__slug__in=brands)
        return queryset

    def filter_min_price(self, queryset, name, value):
        if value:
            return queryset.filter(base_price__gte=value)
        return queryset

    def filter_max_price(self, queryset, name, value):
        if value:
            return queryset.filter(base_price__lte=value)
        return queryset

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(english_title__icontains=value)
            )
        return queryset

    def filter_has_discount(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                Q(discount_percent__gt=0) | 
                Q(
                    special_discount_percent__gt=0,
                    special_offer_end__isnull=False,
                    special_offer_end__gt=now
                )
            ).distinct()
        return queryset

    def filter_is_special_offer(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                special_discount_percent__gt=0,
                special_offer_end__isnull=False,
                special_offer_end__gt=now
            )
        return queryset
        
    def filter_has_stock(self, queryset, name, value):
        if value:
            return queryset.filter(base_inventory__gt=0)
        elif value is False:
            return queryset.filter(base_inventory=0)
        return queryset