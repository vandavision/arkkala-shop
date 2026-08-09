from celery import shared_task
import logging
from shop.models.outbox import OutboxEvent

logger = logging.getLogger(__name__)

@shared_task
def process_outbox_events() -> None:
    """Fetches unprocessed Outbox events and executes handlers asynchronously."""
    events = OutboxEvent.objects.filter(is_processed=False).order_by('created_at')[:50]
    
    for event in events:
        try:
            logger.info(f"Processing Event Async: {event.event_type} | Payload: {event.payload}")
            event.is_processed = True
            event.save(update_fields=['is_processed'])
        except Exception as e:
            logger.error(f"Error processing OutboxEvent ID {event.uuid}: {e}")