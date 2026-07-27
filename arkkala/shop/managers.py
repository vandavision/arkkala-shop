# shop/managers.py
from typing import Optional
from django.db import models
from django.db.models import Prefetch, Exists, OuterRef, Value, BooleanField
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductQuerySet(models.QuerySet):
    """Encapsulates complex querying logic for Product model."""

    def active(self) -> 'ProductQuerySet':
        return self.filter(is_active=True)

    def with_relations(self) -> 'ProductQuerySet':
        return self.select_related('brand', 'category').prefetch_related(
            'variants__attribute_values',
            'gallery',
            'videos',
            'price_history'
        )

    def with_approved_feedback(self) -> 'ProductQuerySet':
        from .models.interaction import Comment, Question
        return self.prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.filter(is_approved=True),
                to_attr='approved_comments'
            ),
            Prefetch(
                'questions',
                queryset=Question.objects.filter(is_approved=True),
                to_attr='approved_questions'
            )
        )

    def with_user_favorite(self, user: Optional[User]) -> 'ProductQuerySet':
        if user and user.is_authenticated:
            from .models.product import Product
            favorite_subquery = Product.favorites.through.objects.filter(
                product_id=OuterRef('pk'),
                user_id=user.id
            )
            return self.annotate(is_user_favorite=Exists(favorite_subquery))
        return self.annotate(is_user_favorite=Value(False, output_field=BooleanField()))


ProductManager = models.Manager.from_queryset(ProductQuerySet)