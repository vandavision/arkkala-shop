"""
Celery Tasks for the Users App.
"""
import logging
from celery import shared_task
from .models import OTPRequest

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_otps(otp_uuid: str) -> str:
    """
    Deletes an OTP request from the database after its expiration time.
    This keeps the database clean and prevents table bloat.

    Args:
        otp_uuid (str): The UUID of the OTPRequest to delete.

    Returns:
        str: Result message.
    """
    try:
        otp_qs = OTPRequest.objects.filter(uuid=otp_uuid)
        if otp_qs.exists():
            otp_qs.delete()
            msg = f"OTP {otp_uuid} was successfully deleted from the database."
            logger.info(msg)
            return msg
        else:
            msg = f"OTP {otp_uuid} not found. Perhaps already deleted."
            logger.info(msg)
            return msg
    except Exception as e:
        error_msg = f"Failed to delete OTP {otp_uuid}: {str(e)}"
        logger.error(error_msg)
        raise e