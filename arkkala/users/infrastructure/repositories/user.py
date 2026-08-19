from typing import Optional, Tuple, Any
from django.contrib.auth import get_user_model
from users.application.ports.repositories import UserRepositoryPort

User = get_user_model()

class UserRepositoryImpl(UserRepositoryPort):
    """
    Concrete implementation abstracting ORM data flows inherently matching definitions.
    """
    def get_by_email(self, email: str) -> Optional[Any]:
        if not email:
            return None
        return User.objects.filter(email__iexact=email.strip()).first()

    def get_or_create_by_phone(self, phone: str) -> Tuple[Any, bool]:
        clean_phone = phone.strip() if phone else ''
        return User.objects.get_or_create(
            phone_number=clean_phone,
            defaults={'username': clean_phone, 'is_active': True}
        )

    def save_user(self, user: Any) -> None:
        user.full_clean()
        user.save()