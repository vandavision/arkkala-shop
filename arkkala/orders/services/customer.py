from typing import Optional, Dict, Any, Tuple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from orders.domain.exceptions import OrderDomainException

User = get_user_model()


class CustomerService:
    @staticmethod
    def resolve_checkout_user(
        user: Optional[AbstractUser], 
        guest_data: Dict[str, Any]
    ) -> Tuple[Optional[AbstractUser], bool]:
        """
        Resolves checkout user securely.
        Returns (resolved_user, should_issue_token).
        """
        if user and user.is_authenticated:
            return user, False

        guest_email = guest_data.get('email')
        guest_phone = guest_data.get('phone')
        guest_password = guest_data.get('password')
        
        if not guest_email and not guest_phone:
            return None, False

        existing_user = None
        if guest_email:
            existing_user = User.objects.filter(email=guest_email).first()
        if not existing_user and guest_phone:
            existing_user = User.objects.filter(phone_number=guest_phone).first()

        if existing_user:
            if guest_password:
                if existing_user.check_password(guest_password):
                    CustomerService._update_missing_fields(existing_user, guest_data)
                    return existing_user, True
                else:
                    raise OrderDomainException("این ایمیل یا شماره موبایل قبلاً در سیستم ثبت شده است. رمز عبور وارد شده اشتباه است.")
            else:
                raise OrderDomainException("این ایمیل یا شماره موبایل در سیستم وجود دارد. لطفاً ابتدا وارد حساب خود شوید یا رمز عبور خود را وارد کنید.")

        defaults = {
            'first_name': guest_data.get('first_name', ''),
            'last_name': guest_data.get('last_name', ''),
            'is_active': True,
            'username': guest_email or guest_phone
        }
        
        if guest_email:
            defaults['email'] = guest_email
        if guest_phone:
            defaults['phone_number'] = guest_phone

        new_user = User(**defaults)
        if guest_password:
            new_user.set_password(guest_password)
        else:
            new_user.set_unusable_password()
        new_user.save()

        return new_user, True

    @staticmethod
    def _update_missing_fields(user: AbstractUser, guest_data: Dict[str, Any]) -> None:
        """Updates user profile if they left fields blank during initial registration."""
        update_fields = []
        mapping = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'phone_number': 'phone'
        }
        
        for user_field, guest_field in mapping.items():
            if hasattr(user, user_field) and not getattr(user, user_field):
                guest_value = guest_data.get(guest_field)
                if guest_value:
                    setattr(user, user_field, guest_value)
                    update_fields.append(user_field)
                    
        if update_fields:
            user.save(update_fields=update_fields)