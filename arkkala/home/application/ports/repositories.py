from abc import ABC, abstractmethod
from home.models.contact_message import ContactMessage

class ContactRepository(ABC):
    """
    Port for managing contact messages persistence.
    """
    @abstractmethod
    def save(self, contact_message: ContactMessage) -> None:
        pass