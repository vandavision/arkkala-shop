from dataclasses import dataclass

@dataclass(frozen=True)
class OTPSendDTO:
    """
    Data Transfer Object for sending an OTP request.
    """
    identifier: str
    ip_address: str
    is_email_reset: bool = False

@dataclass(frozen=True)
class OTPVerifyDTO:
    """
    Data Transfer Object for verifying an OTP and logging in.
    """
    identifier: str
    code: str

@dataclass(frozen=True)
class EmailRegisterDTO:
    """
    Data Transfer Object for standard email registration.
    """
    email: str
    password: str

@dataclass(frozen=True)
class PasswordResetConfirmDTO:
    """
    Data Transfer Object for executing password reset.
    """
    email: str
    code: str
    new_password: str