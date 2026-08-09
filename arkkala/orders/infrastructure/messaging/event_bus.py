from orders.application.ports.event_bus import EventBus
from orders.events.handlers import OrderEventHandler


class DjangoEventBus(EventBus):
    """Simple synchronous event bus for Django."""
    
    def publish(self, event: object) -> None:
        handler = OrderEventHandler()
        handler.handle(event)