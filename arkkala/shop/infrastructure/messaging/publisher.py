import logging
from typing import Any
from django.db import transaction
from shop.application.ports.event_bus import EventBusPort
from shop.application.ports.repositories import OutboxRepositoryPort

logger = logging.getLogger(__name__)

class OutboxDomainEventPublisher(EventBusPort):
    """Transactional Outbox Publisher ensuring atomic event persistence."""
    
    def __init__(self, outbox_repo: OutboxRepositoryPort) -> None:
        self.outbox_repo = outbox_repo

    def publish(self, event: Any) -> None:
        """Saves event natively in DB during the same transaction commit phase."""
        event_type = event.__class__.__name__
        payload = event.__dict__
        
        transaction.on_commit(
            lambda: self._persist_event(event_type, payload)
        )

    def _persist_event(self, event_type: str, payload: dict) -> None:
        """Private method to handle the actual outbox persistence safely."""
        try:
            self.outbox_repo.save_event(event_type, payload)
        except Exception as e:
            logger.error(f"Failed to save Outbox Event {event_type}: {e}")