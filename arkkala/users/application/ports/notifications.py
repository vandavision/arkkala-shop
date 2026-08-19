from typing import Protocol

class SMSProviderPort(Protocol):
    """
    Abstract interface for executing transactional SMS broadcasts securely.
    """
    def send_verification_code(self, phone_number: str, code: str) -> bool: ...

class EmailProviderPort(Protocol):
    """
    Abstract interface encapsulating asynchronous email dispatches strictly.
    """
    def send_password_reset(self, email: str, code: str) -> bool: ...