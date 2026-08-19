from typing import Any
from users.application.ports.repositories import OTPRepositoryPort

class CleanupOTPCommand:
    """
    Use case responsible for flushing expired transient authentications structurally.
    """
    def __init__(self, otp_repo: OTPRepositoryPort) -> None:
        self.otp_repo = otp_repo

    def execute(self, otp_uuid: Any) -> None:
        """
        Delegates atomic deletion ensuring no business rules leak.
        """
        self.otp_repo.delete_by_uuid(otp_uuid)