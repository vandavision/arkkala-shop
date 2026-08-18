from typing import Optional
from orders.models.order import Order
from payments.application.ports.repositories import PaymentOrderRepository
from shop.services.interaction import InteractionService

class DjangoPaymentOrderRepository(PaymentOrderRepository):
    def get_order_by_uuid(self, uuid: str) -> Optional[Order]:
        return Order.objects.filter(uuid=uuid).first()

    def mark_order_as_paid(self, order: Order, tracking_code: str) -> None:
        order.is_paid = True
        order.status = 'paid'
        order.tracking_code = tracking_code
        order.save(update_fields=['is_paid', 'status', 'tracking_code'])

        if getattr(order, 'user', None):
            for item in order.items.select_related('product').all():
                if item.product:
                    InteractionService.record_product_purchase(order.user, item.product, 5)