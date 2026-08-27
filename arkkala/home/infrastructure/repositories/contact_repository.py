from home.application.ports.repositories import ContactRepository
from home.models.contact_message import ContactMessage

class DjangoContactRepository(ContactRepository):
    """
    Django ORM implementation for ContactRepository.
    """
    def save(self, contact_message: ContactMessage) -> None:
        contact_message.save()