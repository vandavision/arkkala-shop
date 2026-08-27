from django.db import transaction
from home.application.dto.commands import SubmitContactMessageDTO
from home.application.ports.repositories import ContactRepository
from home.models.contact_message import ContactMessage

class SubmitContactMessageCommand:
    """
    Use case for submitting a new contact message.
    """
    def __init__(self, repository: ContactRepository) -> None:
        self.repository = repository

    @transaction.atomic
    def execute(self, dto: SubmitContactMessageDTO) -> None:
        contact_message = ContactMessage(
            full_name=dto.full_name,
            phone_number=dto.phone_number,
            email=dto.email,
            subject=dto.subject,
            message=dto.message,
            is_read=False
        )
        self.repository.save(contact_message)