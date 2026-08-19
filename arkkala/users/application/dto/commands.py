from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class OTPSendDTO:
    identifier: str
    ip_address: str
    is_email_reset: bool = False

@dataclass(frozen=True)
class OTPVerifyDTO:
    identifier: str
    code: str
    guest_id: Optional[str] = None
    client_ip: Optional[str] = None

@dataclass(frozen=True)
class EmailRegisterDTO:
    email: str
    password: str
    guest_id: Optional[str] = None
    client_ip: Optional[str] = None

@dataclass(frozen=True)
class EmailLoginDTO:
    email: str
    password: str
    guest_id: Optional[str] = None
    client_ip: Optional[str] = None

@dataclass(frozen=True)
class PasswordResetConfirmDTO:
    email: str
    code: str
    new_password: str

@dataclass(frozen=True)
class SetDefaultAddressDTO:
    user_id: int
    address_uuid: str