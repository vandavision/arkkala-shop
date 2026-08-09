from typing import Dict, Any
from shop.models.outbox import OutboxEvent
from shop.application.ports.repositories import OutboxRepositoryPort

class DjangoOutboxRepository(OutboxRepositoryPort):
    """Django ORM Implementation of Outbox Repository Port."""

    def save_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Persists the event payload safely into the Outbox table."""
        OutboxEvent.objects.create(
            event_type=event_type,
            payload=payload,
            is_processed=False
        )