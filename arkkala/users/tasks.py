import logging
from celery import shared_task
from users.repositories.otp import OTPRepository

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_otps(otp_uuid: str) -> str:
    """
    Executes precise removal of sensitive request hashes cleanly to minimize DB bloat.
    """
    try:
        repo = OTPRepository()
        otp_obj = repo.get_by_uuid(otp_uuid)
        if otp_obj:
            repo.delete(otp_obj)
            msg: str = f"OTP {otp_uuid} was successfully deleted from the database."
            logger.info(msg)
            return msg
        msg = f"OTP {otp_uuid} not found. Perhaps already deleted."
        logger.info(msg)
        return msg
    except Exception as e:
        error_msg: str = f"Failed to delete OTP {otp_uuid}: {str(e)}"
        logger.error(error_msg)
        raise e