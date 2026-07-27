# shop/views/__init__.py
from .product import ProductViewSet, MaxPriceAPIView
from .interaction import CommentViewSet

__all__ = ['ProductViewSet', 'MaxPriceAPIView', 'CommentViewSet']