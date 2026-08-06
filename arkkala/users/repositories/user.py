from typing import Optional, Tuple
from django.contrib.auth import get_user_model
from users.repositories.base import BaseRepository

User = get_user_model()

class UserRepository(BaseRepository[User]):
    """
    Data abstraction layer for the User domain.
    """
    def __init__(self) -> None:
        """
        Initializes the User repository.
        """
        super().__init__(User)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Fetches user by exact email.
        """
        return self.model.objects.filter(email=email).first()

    def get_or_create_by_phone(self, phone: str) -> Tuple[User, bool]:
        """
        Retrieves or safely initializes a user by phone.
        """
        return self.model.objects.get_or_create(
            phone_number=phone,
            defaults={'username': phone, 'is_active': True}
        )