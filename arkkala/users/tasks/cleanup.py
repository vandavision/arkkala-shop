import logging
from celery import shared_task
from users.dependencies import cleanup_otp_command

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_otps(otp_uuid: str) -> str:
    """
    Executes precise removal of sensitive request hashes cleanly minimizing DB bloat.
    """
    try:
        cleanup_otp_command.execute(otp_uuid)
        msg: str = f"OTP {otp_uuid} was successfully processed for deletion."
        logger.info(msg)
        return msg
    except Exception as e:
        error_msg: str = f"Failed to delete OTP {otp_uuid}: {str(e)}"
        logger.error(error_msg)
        raise e