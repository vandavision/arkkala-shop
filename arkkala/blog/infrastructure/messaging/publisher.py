import logging
from typing import Any
from blog.application.ports.event_bus import EventBusPort

logger = logging.getLogger(__name__)

class DjangoEventPublisher(EventBusPort):
    def publish(self, event: Any) -> None:
        logger.info(f"Domain Event Dispatched: {event.name} | Payload: {event.payload}")