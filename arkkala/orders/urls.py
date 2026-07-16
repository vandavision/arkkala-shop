"""
URL Routings for Orders App.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.cart import CartViewSet
from .views.order import OrderViewSet, OrderRequestViewSet
from .views.shipping import ShippingMethodViewSet

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-requests', OrderRequestViewSet, basename='order-requests')
router.register(r'shipping-methods', ShippingMethodViewSet, basename='shipping-methods')

urlpatterns = [
    path('', include(router.urls)),
]