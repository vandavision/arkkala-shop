from typing import Dict, Any
from .models import ContactMessage


class ContactService:
    """Business logic for handling Contact Us messages."""
    
    @staticmethod
    def create_message(validated_data: Dict[str, Any]) -> ContactMessage:
        """
        Creates a new contact message.
        Future extension: Trigger Email/SMS notification to site admins here.
        """
        message = ContactMessage.objects.create(**validated_data)
        return message