from typing import Optional, Tuple
from django.contrib.auth import get_user_model
from users.repositories.base import BaseRepository

User = get_user_model()

class UserRepository(BaseRepository[User]):
    """
    Data abstraction layer for the User domain.
    """
    def __init__(self) -> None:
        super().__init__(User)

    def get_by_email(self, email: str) -> Optional[User]:
        if not email:
            return None
        return self.model.objects.filter(email__iexact=email.strip()).first()

    def get_or_create_by_phone(self, phone: str) -> Tuple[User, bool]:
        clean_phone = phone.strip() if phone else ''
        return self.model.objects.get_or_create(
            phone_number=clean_phone,
            defaults={'username': clean_phone, 'is_active': True}
        )