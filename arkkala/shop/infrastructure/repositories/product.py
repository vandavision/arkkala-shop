from typing import Optional, Any, List, Dict, Set, Tuple
from django.db.models import F, Max, QuerySet, Q, Case, When, Value, IntegerField
from django.apps import apps
from shop.models.product import Product, ProductFavorite
from shop.models.interaction import UserProductHistory
from shop.application.ports.repositories import ProductRepositoryPort
from shop.repositories.base import BaseRepository


class RecommendationScoringConfig:
    MAX_VIEW_COUNT: int = 15
    VIEW_BASE_WEIGHT: int = 3
    ORDER_BASE_WEIGHT: int = 15
    TOP_CATEGORIES_LIMIT: int = 5
    TOP_BRANDS_LIMIT: int = 5
    RECOMMENDATION_LIMIT: int = 10


class DjangoProductRepository(ProductRepositoryPort, BaseRepository[Product]):
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
        base_qs = self.get_active_products_optimized(user)
        history_list, order_list = self._fetch_recent_interactions(user, guest_id)

        if not history_list and not order_list:
            return self._get_fallback_recommendations(base_qs)

        cat_weights, brand_weights, historical_ids = self._calculate_affinity_scores(history_list, order_list)

        top_categories = self._extract_top_keys(cat_weights, RecommendationScoringConfig.TOP_CATEGORIES_LIMIT)
        top_brands = self._extract_top_keys(brand_weights, RecommendationScoringConfig.TOP_BRANDS_LIMIT)

        if not top_categories and not top_brands:
            return self._get_fallback_recommendations(base_qs.exclude(uuid__in=historical_ids))

        scored_qs = self._build_scored_recommendation_query(
            base_qs=base_qs,
            top_cats=top_categories,
            top_brands=top_brands,
            cat_weights=cat_weights,
            brand_weights=brand_weights,
            excluded_ids=historical_ids
        )

        mixed_qs = self._mix_results_by_category(base_qs, scored_qs, RecommendationScoringConfig.RECOMMENDATION_LIMIT)
        
        if not mixed_qs.exists():
            return self._get_fallback_recommendations(base_qs.exclude(uuid__in=historical_ids))

        return mixed_qs

    def _mix_results_by_category(self, base_qs: QuerySet, scored_qs: QuerySet, limit: int) -> QuerySet:
        pool = list(scored_qs[:40])
        if not pool:
            return base_qs.none()

        grouped = {}
        for p in pool:
            cat = getattr(p, 'category_id', 'unknown')
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(p)
            
        sorted_cat_ids = sorted(grouped.keys(), key=lambda c: grouped[c][0].total_match_score, reverse=True)

        mixed_uuids = []
        while len(mixed_uuids) < limit and grouped:
            for cat in list(sorted_cat_ids):
                if len(mixed_uuids) >= limit:
                    break
                
                if cat in grouped and grouped[cat]:
                    item = grouped[cat].pop(0)
                    mixed_uuids.append(item.uuid)
                    
                    if not grouped[cat]:
                        del grouped[cat]
                        sorted_cat_ids.remove(cat)

        if not mixed_uuids:
            return base_qs.none()

        preserved_order = Case(*[When(uuid=pk, then=Value(pos)) for pos, pk in enumerate(mixed_uuids)], output_field=IntegerField())
        return base_qs.filter(uuid__in=mixed_uuids).order_by(preserved_order)


    def _fetch_recent_interactions(self, user: Any, guest_id: Optional[str]) -> Tuple[List[Any], List[Any]]:
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
        cat_weights: Dict[Any, int] = {}
        brand_weights: Dict[Any, int] = {}
        historical_ids: Set[Any] = set()
        cfg = RecommendationScoringConfig

        for idx, history in enumerate(history_list):
            recency_multiplier = max(1, 4 - (idx // 5))
            calc_weight = min(history.view_count, cfg.MAX_VIEW_COUNT) * cfg.VIEW_BASE_WEIGHT * recency_multiplier
            
            historical_ids.add(history.product.uuid)
            if history.product.category_id:
                cat_weights[history.product.category_id] = cat_weights.get(history.product.category_id, 0) + calc_weight
            if history.product.brand_id:
                brand_weights[history.product.brand_id] = brand_weights.get(history.product.brand_id, 0) + calc_weight

        for idx, order in enumerate(order_list):
            recency_multiplier = max(1, 3 - (idx // 3))
            quantity = getattr(order, 'quantity', 1)
            calc_weight = quantity * cfg.ORDER_BASE_WEIGHT * recency_multiplier
            
            historical_ids.add(order.product.uuid)
            if order.product.category_id:
                cat_weights[order.product.category_id] = cat_weights.get(order.product.category_id, 0) + calc_weight
            if order.product.brand_id:
                brand_weights[order.product.brand_id] = brand_weights.get(order.product.brand_id, 0) + calc_weight

        return cat_weights, brand_weights, historical_ids

    def _extract_top_keys(self, weights_dict: Dict[Any, int], limit: int) -> List[Any]:
        return sorted(weights_dict, key=weights_dict.get, reverse=True)[:limit]

    def _get_fallback_recommendations(self, base_qs: QuerySet) -> QuerySet:
        return base_qs.order_by('-view_count', '-sold_count')[:RecommendationScoringConfig.RECOMMENDATION_LIMIT]

    def _build_scored_recommendation_query(
        self, base_qs: QuerySet, top_cats: List[Any], top_brands: List[Any],
        cat_weights: Dict[Any, int], brand_weights: Dict[Any, int], excluded_ids: Set[Any]
    ) -> QuerySet:
        filter_q = Q()
        
        if top_cats:
            filter_q |= Q(category_id__in=top_cats)
        if top_brands:
            filter_q |= Q(brand_id__in=top_brands)

        qs = base_qs.filter(filter_q).exclude(uuid__in=excluded_ids)

        cat_cases = [When(category_id=cid, then=Value(cat_weights.get(cid, 0))) for cid in top_cats]
        brand_cases = [When(brand_id=bid, then=Value(brand_weights.get(bid, 0))) for bid in top_brands]

        qs = qs.annotate(
            user_cat_score=Case(*cat_cases, default=Value(0), output_field=IntegerField()) if cat_cases else Value(0, output_field=IntegerField()),
            user_brand_score=Case(*brand_cases, default=Value(0), output_field=IntegerField()) if brand_cases else Value(0, output_field=IntegerField()),
            offer_boost=Case(When(special_discount_percent__gt=0, then=Value(50)), default=Value(0), output_field=IntegerField())
        )

        return qs.annotate(
            total_match_score=F('user_cat_score') + F('user_brand_score') + F('offer_boost')
        ).order_by('-total_match_score', '-sold_count')