from typing import Optional, Dict, Any, Tuple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

User = get_user_model()


class CustomerService:
    """Service to handle Guest vs Authenticated user logic and syncing."""

    @staticmethod
    def resolve_checkout_user(
        user: Optional[AbstractUser], 
        guest_data: Dict[str, Any]
    ) -> Optional[AbstractUser]:
        """
        Resolves or creates a user based on checkout data.
        Updates user attributes dynamically if they are missing.
        """
        if not user:
            guest_email = guest_data.get('guest_email')
            guest_phone = guest_data.get('guest_phone')
            guest_password = guest_data.get('guest_password')
            
            defaults = {
                'first_name': guest_data.get('guest_first_name', ''),
                'last_name': guest_data.get('guest_last_name', ''),
                'is_active': True
            }

            if guest_email and guest_password:
                defaults['username'] = guest_email
                user, created = User.objects.get_or_create(email=guest_email, defaults=defaults)
                if created:
                    user.set_password(guest_password)
                    user.save()
            elif guest_phone:
                defaults['username'] = guest_phone
                user, _ = User.objects.get_or_create(phone_number=guest_phone, defaults=defaults)

        if user:
            CustomerService._update_missing_fields(user, guest_data)

        return user

    @staticmethod
    def _update_missing_fields(user: AbstractUser, guest_data: Dict[str, Any]) -> None:
        """Helper to fill missing user fields gracefully."""
        update_fields = []
        mapping = {
            'first_name': 'guest_first_name',
            'last_name': 'guest_last_name',
            'phone_number': 'guest_phone'
        }
        
        for user_field, guest_field in mapping.items():
            if hasattr(user, user_field) and not getattr(user, user_field):
                guest_value = guest_data.get(guest_field)
                if guest_value:
                    setattr(user, user_field, guest_value)
                    update_fields.append(user_field)
                    
        if update_fields:
            user.save(update_fields=update_fields)