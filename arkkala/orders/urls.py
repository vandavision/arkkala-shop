from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, ShippingMethodViewSet

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'shipping-methods', ShippingMethodViewSet, basename='shipping-methods')

urlpatterns = [
    path('', include(router.urls)),
]