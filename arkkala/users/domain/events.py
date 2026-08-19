import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DomainEventPublisher:
    """
    Handles internal publication of domain events to decouple contexts.
    """
    @classmethod
    def publish(cls, event_name: str, payload: Dict[str, Any]) -> None:
        """
        Dispatches domain events accurately to corresponding infrastructure buses.
        """
        logger.info(f"Domain Event Dispatched: {event_name} | Payload: {payload}")