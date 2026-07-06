"""
URLs mapping for Shop App.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, MaxPriceAPIView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('max-price/', MaxPriceAPIView.as_view(), name='max-price'),
    path('', include(router.urls)),
]