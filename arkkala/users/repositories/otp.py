from typing import Optional
from django.utils import timezone
from users.models.otp import OTPRequest
from users.repositories.base import BaseRepository

class OTPRepository(BaseRepository[OTPRequest]):
    """
    Data abstraction layer for OTP logic and rate limit tracking.
    """
    def __init__(self) -> None:
        """
        Initializes the OTP repository.
        """
        super().__init__(OTPRequest)

    def get_valid_otp(self, identifier: str, code: str) -> Optional[OTPRequest]:
        """
        Retrieves an unused and unexpired OTP for the given identifier.
        """
        return self.model.objects.filter(
            identifier=identifier,
            code=code,
            is_used=False,
            expires_at__gte=timezone.now()
        ).first()

    def count_recent_requests(self, identifier: str, since: timezone.datetime) -> int:
        """
        Counts total OTP requests made by an identifier since a specific datetime.
        """
        return self.model.objects.filter(
            identifier=identifier,
            created_at__gte=since
        ).count()

    def get_last_request(self, identifier: str) -> Optional[OTPRequest]:
        """
        Retrieves the latest OTP request made by the identifier.
        """
        return self.model.objects.filter(identifier=identifier).order_by('-created_at').first()