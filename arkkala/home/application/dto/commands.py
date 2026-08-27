from dataclasses import dataclass

@dataclass(frozen=True)
class SubmitContactMessageDTO:
    """
    Data Transfer Object for submitting a contact message.
    """
    full_name: str
    phone_number: str
    email: str
    subject: str
    message: str