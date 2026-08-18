import logging
from orders.domain.events import OrderCreatedEvent
from platform_tools.services.email import EmailService
from orders.tasks import cancel_unpaid_order
from orders.models.order import Order

logger = logging.getLogger(__name__)


class OrderEventHandler:
    """Handles domain events emitted by the orders application."""

    def handle(self, event: object) -> None:
        if isinstance(event, OrderCreatedEvent):
            self._handle_order_created(event)

    def _handle_order_created(self, event: OrderCreatedEvent) -> None:
        if event.user_email:
            try:
                order = Order.objects.get(uuid=event.order_uuid)
                EmailService.send_order_invoice(order=order, user_email=event.user_email)
            except Order.DoesNotExist:
                logger.error(f"Order with UUID {event.order_uuid} not found for sending invoice.")
            except Exception as e:
                logger.error(f"Failed to send email invoice for order {event.order_uuid}: {str(e)}")

        cancel_unpaid_order.apply_async((event.order_uuid,), countdown=7200)