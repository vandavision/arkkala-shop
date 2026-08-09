from typing import Optional
from django.utils import timezone
from django.db.models import F
from orders.models.coupon import Coupon
from orders.application.ports.repositories import CouponRepository


class DjangoCouponRepository(CouponRepository):
    """Django ORM implementation of CouponRepository."""

    def get_valid_coupon(self, code: str, lock: bool = False) -> Optional[Coupon]:
        now = timezone.now()
        qs = Coupon.objects.filter(
            code__iexact=code,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
            used_count__lt=F('usage_limit')
        )
        if lock:
            qs = qs.select_for_update()
        return qs.first()

    def increment_usage(self, coupon: Coupon) -> None:
        coupon.used_count = F('used_count') + 1
        coupon.save(update_fields=['used_count'])