from decimal import Decimal
from typing import Optional, Tuple
from django.utils import timezone
from django.db.models import F
from orders.models import Coupon


class CouponService:
    """Business logic for validating and applying coupons."""
    
    @staticmethod
    def validate_coupon(code: str, lock_for_update: bool = False) -> Coupon:
        """Validates coupon state against limits and dates."""
        now = timezone.now()
        qs = Coupon.objects.filter(
            code__iexact=code,
            is_active=True,
            valid_from__lte=now,
            valid_to__gte=now,
            used_count__lt=F('usage_limit')
        )
        
        if lock_for_update:
            qs = qs.select_for_update()
            
        coupon: Optional[Coupon] = qs.first()
        if not coupon:
            raise ValueError("کد تخفیف نامعتبر است یا ظرفیت آن پر شده/منقضی شده است.")
            
        return coupon

    @staticmethod
    def apply_coupon(coupon_code: str, total_items_amount: Decimal) -> Tuple[Optional[Coupon], Decimal]:
        """Calculates discount amount and applies usage increment safely."""
        coupon_obj = CouponService.validate_coupon(coupon_code, lock_for_update=True)
        
        discount = (total_items_amount * coupon_obj.discount_percent) / Decimal(100)
        if coupon_obj.max_discount_amount and discount > coupon_obj.max_discount_amount:
            discount = coupon_obj.max_discount_amount

        coupon_obj.used_count = F('used_count') + 1
        coupon_obj.save(update_fields=['used_count'])
        
        return coupon_obj, discount