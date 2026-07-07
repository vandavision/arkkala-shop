"""
Celery Tasks for the Orders App.
Contains background jobs such as auto-cancelling unpaid orders.
"""
import logging
from celery import shared_task
from django.db import transaction
from django.db.models import F

from .models import Order

logger = logging.getLogger(__name__)


@shared_task
def cancel_unpaid_order(order_uuid: str) -> str:
    """
    Checks if an order is still 'pending' after a specific time limit.
    If it is, the order is cancelled and the reserved inventory is restored.

    Args:
        order_uuid (str): The UUID of the order to check.

    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().filter(
                uuid=order_uuid,
                status='pending'
            ).first()

            if not order:
                msg: str = f"Order {order_uuid} is not pending or does not exist."
                logger.info(msg)
                return msg

            order.status = 'cancelled'
            order.save(update_fields=['status'])

            for item in order.items.select_related('product', 'variant').all():
                if item.variant:
                    item.variant.inventory = F('inventory') + item.quantity
                    item.variant.save(update_fields=['inventory'])
                elif item.product:
                    item.product.base_inventory = F('base_inventory') + item.quantity
                    item.product.save(update_fields=['base_inventory'])

            success_msg: str = f"Order {order_uuid} auto-cancelled and inventory restored."
            logger.info(success_msg)
            return success_msg

    except Exception as e:
        error_msg: str = f"Error cancelling unpaid order {order_uuid}: {str(e)}"
        logger.error(error_msg)
        raise e