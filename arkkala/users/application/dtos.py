from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class OTPSendDTO:
    """
    Data Transfer Object for sending an OTP request securely.
    """
    identifier: str
    ip_address: str
    is_email_reset: bool = False

@dataclass(frozen=True)
class OTPVerifyDTO:
    """
    Data Transfer Object for verifying an OTP structure and tracking guest identity.
    """
    identifier: str
    code: str
    guest_id: Optional[str] = None
    client_ip: Optional[str] = None

@dataclass(frozen=True)
class EmailRegisterDTO:
    """
    Data Transfer Object for mapping basic email registration inputs natively.
    """
    email: str
    password: str
    guest_id: Optional[str] = None
    client_ip: Optional[str] = None

@dataclass(frozen=True)
class EmailLoginDTO:
    """
    Data Transfer Object for passing raw credentials towards internal CQRS commands.
    """
    email: str
    password: str
    guest_id: Optional[str] = None
    client_ip: Optional[str] = None

@dataclass(frozen=True)
class PasswordResetConfirmDTO:
    """
    Data Transfer Object securing execution for password overwriting procedures.
    """
    email: str
    code: str
    new_password: str