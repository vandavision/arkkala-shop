"""
URLs mapping for Search App.
"""
from django.urls import path
from .views import GlobalSearchView, CategoryTreeView, BrandBrowseView

urlpatterns = [
    path('global/', GlobalSearchView.as_view(), name='global-search'),
    path('categories/tree/', CategoryTreeView.as_view(), name='category-tree'),
    path('brands/', BrandBrowseView.as_view(), name='brand-browse'),
]