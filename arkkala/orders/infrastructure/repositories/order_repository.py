from typing import Optional, List
from orders.models.order import Order, OrderItem, OrderRequest
from orders.application.ports.repositories import OrderRepository


class DjangoOrderRepository(OrderRepository):
    """Django ORM implementation of OrderRepository."""

    def create_order(self, order_data: dict) -> Order:
        return Order.objects.create(**order_data)

    def create_order_items(self, order_items_data: List[dict]) -> None:
        items = [OrderItem(**data) for data in order_items_data]
        OrderItem.objects.bulk_create(items)

    def get_user_order(self, user_id: int, order_uuid: str) -> Optional[Order]:
        return Order.objects.filter(user_id=user_id, uuid=order_uuid).first()

    def create_order_request(self, order: Order, request_type: str, reason: str) -> OrderRequest:
        return OrderRequest.objects.create(
            order=order,
            request_type=request_type,
            reason=reason,
            status=OrderRequest.StatusChoices.PENDING
        )