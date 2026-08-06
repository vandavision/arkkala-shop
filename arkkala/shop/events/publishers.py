import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DomainEventPublisher:
    """
    Event Broker interface for asynchronous architecture (e.g., passing to RabbitMQ/Kafka in the future).
    """
    @classmethod
    def publish(cls, event_name: str, payload: Dict[str, Any]) -> None:
        logger.info(f"Domain Event Dispatched: {event_name} | Payload: {payload}")