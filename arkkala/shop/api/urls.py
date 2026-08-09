from django.urls import path, include
from rest_framework.routers import DefaultRouter
from shop.api.views.product import ProductViewSet, MaxPriceAPIView
from shop.api.views.interaction import CommentViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns: list = [
    path('max-price/', MaxPriceAPIView.as_view(), name='max-price'),
    path('', include(router.urls)),
]