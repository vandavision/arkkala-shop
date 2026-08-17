from typing import Optional, Any, List, Dict, Set, Tuple
from django.db.models import F, Max, QuerySet, Q, Case, When, Value, IntegerField
from django.apps import apps
from shop.models.product import Product, ProductFavorite
from shop.models.interaction import UserProductHistory
from shop.application.ports.repositories import ProductRepositoryPort
from shop.repositories.base import BaseRepository


class RecommendationScoringConfig:
    """
    Configuration constants for recommendation scoring weights.
    Adheres to the Open/Closed Principle (OCP).
    """
    MAX_VIEW_COUNT: int = 10
    VIEW_WEIGHT_MULTIPLIER: int = 1
    MAX_ORDER_QUANTITY: int = 5
    ORDER_WEIGHT_MULTIPLIER: int = 5
    TOP_CATEGORIES_LIMIT: int = 4
    TOP_BRANDS_LIMIT: int = 4
    RECOMMENDATION_LIMIT: int = 10


class DjangoProductRepository(ProductRepositoryPort, BaseRepository[Product]):
    """Django ORM Implementation of Product Repository Port adhering to SOLID."""

    def __init__(self) -> None:
        super().__init__(Product)

    def get_by_slug(self, slug: str) -> Optional[Product]:
        return Product.objects.filter(slug=slug).first()

    def increment_view_count(self, slug: str) -> bool:
        updated = Product.objects.filter(slug=slug).update(view_count=F('view_count') + 1)
        return updated > 0

    def toggle_favorite(self, product_slug: str, user_id: Any) -> bool:
        product_id = Product.objects.filter(slug=product_slug).values_list('uuid', flat=True).first()
        if not product_id:
            raise ValueError("Product not found")

        deleted_count, _ = ProductFavorite.objects.filter(product_id=product_id, user_id=user_id).delete()
        if deleted_count > 0:
            return False
            
        ProductFavorite.objects.create(product_id=product_id, user_id=user_id)
        return True

    def get_max_base_price(self) -> int:
        result = Product.objects.filter(is_active=True).aggregate(max_price=Max('base_price'))
        return int(result.get('max_price') or 0)

    def get_active_products_optimized(self, user: Any) -> QuerySet:
        qs = Product.objects.active().with_relations().with_approved_feedback()
        return qs.with_user_favorite(user)

    def save_product(self, product: Product) -> Product:
        product.save()
        return product

    def get_recommendations_for_user(self, user: Any, guest_id: Optional[str] = None) -> QuerySet:
        """
        Orchestrates recommendations using Weighted Collaborative Filtering.
        Delegates responsibilities to satisfy the Single Responsibility Principle.
        """
        base_qs = self.get_active_products_optimized(user)
        history_list, order_list = self._fetch_recent_interactions(user, guest_id)

        if not history_list and not order_list:
            return self._get_fallback_recommendations(base_qs)

        cat_weights, brand_weights, historical_ids = self._calculate_affinity_scores(history_list, order_list)

        top_categories = self._extract_top_keys(cat_weights, RecommendationScoringConfig.TOP_CATEGORIES_LIMIT)
        top_brands = self._extract_top_keys(brand_weights, RecommendationScoringConfig.TOP_BRANDS_LIMIT)

        if not top_categories and not top_brands:
            return self._get_fallback_recommendations(base_qs)

        recommendations = self._build_scored_recommendation_query(
            base_qs=base_qs,
            top_cats=top_categories,
            top_brands=top_brands,
            cat_weights=cat_weights,
            brand_weights=brand_weights,
            excluded_ids=historical_ids
        )

        if not recommendations.exists():
            return self._get_fallback_recommendations(base_qs)

        return recommendations


    def _fetch_recent_interactions(self, user: Any, guest_id: Optional[str]) -> Tuple[List[Any], List[Any]]:
        """Isolates the data fetching logic for user interactions."""
        OrderItem = apps.get_model('orders', 'OrderItem')
        history_qs = UserProductHistory.objects.none()
        order_qs = OrderItem.objects.none()

        if user and user.is_authenticated:
            history_qs = UserProductHistory.objects.filter(user=user).select_related('product').order_by('-modified_at')[:20]
            order_qs = OrderItem.objects.filter(order__user=user).select_related('product').order_by('-created_at')[:10]
        elif guest_id:
            history_qs = UserProductHistory.objects.filter(guest_id=guest_id).select_related('product').order_by('-modified_at')[:20]

        return list(history_qs), list(order_qs)

    def _calculate_affinity_scores(self, history_list: List[Any], order_list: List[Any]) -> Tuple[Dict[Any, int], Dict[Any, int], Set[Any]]:
        """Isolates the mathematical scoring algorithm (DRY & SRP)."""
        cat_weights: Dict[Any, int] = {}
        brand_weights: Dict[Any, int] = {}
        historical_ids: Set[Any] = set()
        cfg = RecommendationScoringConfig

        def _apply_weight(product: Product, weight: int) -> None:
            historical_ids.add(product.uuid)
            if product.category_id:
                cat_weights[product.category_id] = cat_weights.get(product.category_id, 0) + weight
            if product.brand_id:
                brand_weights[product.brand_id] = brand_weights.get(product.brand_id, 0) + weight

        for history in history_list:
            calc_weight = min(history.view_count, cfg.MAX_VIEW_COUNT) * cfg.VIEW_WEIGHT_MULTIPLIER
            _apply_weight(history.product, calc_weight)

        for order in order_list:
            quantity = getattr(order, 'quantity', 1)
            calc_weight = min(quantity, cfg.MAX_ORDER_QUANTITY) * cfg.ORDER_WEIGHT_MULTIPLIER
            _apply_weight(order.product, calc_weight)

        return cat_weights, brand_weights, historical_ids

    def _extract_top_keys(self, weights_dict: Dict[Any, int], limit: int) -> List[Any]:
        """Sorts and extracts top IDs from a weight dictionary (DRY)."""
        return sorted(weights_dict, key=weights_dict.get, reverse=True)[:limit]

    def _get_fallback_recommendations(self, base_qs: QuerySet) -> QuerySet:
        """Provides a unified fallback query strategy to avoid code duplication (DRY)."""
        return base_qs.order_by('-view_count', '-sold_count')[:RecommendationScoringConfig.RECOMMENDATION_LIMIT]

    def _build_scored_recommendation_query(
        self, base_qs: QuerySet, top_cats: List[Any], top_brands: List[Any],
        cat_weights: Dict[Any, int], brand_weights: Dict[Any, int], excluded_ids: Set[Any]
    ) -> QuerySet:
        """Constructs the complex annotated QuerySet for dynamic database scoring."""
        filter_q = Q()
        if top_cats:
            filter_q |= Q(category_id__in=top_cats)
        if top_brands:
            filter_q |= Q(brand_id__in=top_brands)

        qs = base_qs.filter(filter_q).exclude(uuid__in=excluded_ids)

        cat_cases = [When(category_id=cid, then=Value(cat_weights[cid])) for cid in top_cats]
        brand_cases = [When(brand_id=bid, then=Value(brand_weights[bid])) for bid in top_brands]

        qs = qs.annotate(
            user_cat_score=Case(*cat_cases, default=Value(0), output_field=IntegerField()) if cat_cases else Value(0, output_field=IntegerField()),
            user_brand_score=Case(*brand_cases, default=Value(0), output_field=IntegerField()) if brand_cases else Value(0, output_field=IntegerField())
        )

        return qs.annotate(
            total_match_score=F('user_cat_score') + F('user_brand_score')
        ).order_by('-total_match_score', '-view_count')[:RecommendationScoringConfig.RECOMMENDATION_LIMIT]