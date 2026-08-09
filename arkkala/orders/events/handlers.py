from orders.domain.events import OrderCreatedEvent
from platform_tools.services.email import EmailService
from orders.tasks import cancel_unpaid_order


class OrderEventHandler:
    """Handles domain events emitted by the orders application."""
    
    def handle(self, event: object) -> None:
        if isinstance(event, OrderCreatedEvent):
            self._handle_order_created(event)

    def _handle_order_created(self, event: OrderCreatedEvent) -> None:
        if event.user_email:
            EmailService.send_order_invoice(order_id=event.order_uuid, user_email=event.user_email)
            
        cancel_unpaid_order.apply_async((event.order_uuid,), countdown=7200)