from typing import Any
from django.utils.timezone import now
from datetime import timedelta
from orders.models import Order, OrderRequest


class OrderRequestService:
    """Handles business logic for processing return and cancellation requests."""
    
    @staticmethod
    def create_request(user: Any, order_id: str, request_type: str, reason: str) -> OrderRequest:
        try:
            order = Order.objects.get(uuid=order_id, user=user)
        except Order.DoesNotExist:
            raise ValueError("سفارش یافت نشد.")
        
        if hasattr(order, 'action_request'):
            raise ValueError("برای این سفارش قبلا درخواست ثبت شده است.")

        if request_type == OrderRequest.RequestTypeChoices.CANCEL:
            if order.status not in ['pending', 'paid', 'processing']:
                raise ValueError("فقط سفارشات در انتظار پرداخت، پرداخت شده یا در حال پردازش قابل لغو هستند.")
        
        elif request_type == OrderRequest.RequestTypeChoices.RETURN:
            if order.status != 'delivered':
                raise ValueError("فقط سفارشات تحویل داده شده قابل مرجوعی هستند.")
            
            if (now() - order.updated_at) > timedelta(days=7):
                raise ValueError("مهلت ۷ روزه مرجوعی این سفارش به پایان رسیده است.")
        else:
            raise ValueError("نوع درخواست نامعتبر است.")

        return OrderRequest.objects.create(
            order=order, request_type=request_type, reason=reason, status=OrderRequest.StatusChoices.PENDING
        )

    @staticmethod
    def process_approved_request(obj: OrderRequest) -> None:
        """Called automatically when an admin approves a request."""
        order_needs_update = False
        
        if obj.request_type == OrderRequest.RequestTypeChoices.CANCEL and obj.order.status != 'cancelled':
            obj.order.status = 'cancelled'
            order_needs_update = True
            
        elif obj.request_type == OrderRequest.RequestTypeChoices.RETURN and obj.order.status != 'returned':
            obj.order.status = 'returned'
            order_needs_update = True
            
        if order_needs_update:
            obj.order.save(update_fields=['status'])