from typing import Optional, Dict, Any, Tuple
from django.conf import settings
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
        if user and user.is_authenticated:
            return user, False

        guest_email = str(guest_data.get('email') or '').strip().lower()
        guest_phone = str(guest_data.get('phone') or '').strip()
        guest_password = str(guest_data.get('password') or '').strip()

        if not guest_email and not guest_phone:
            auth_mode = getattr(settings, 'AUTH_MODE', 'OTP')
            if auth_mode == 'EMAIL':
                raise OrderDomainException("جهت تکمیل فرآیند ثبت سفارش، وارد کردن آدرس ایمیل الزامی است.")
            else:
                raise OrderDomainException("جهت تکمیل فرآیند ثبت سفارش، وارد کردن شماره موبایل الزامی است.")

        existing_user = None
        if guest_email:
            existing_user = User.objects.filter(email__iexact=guest_email).first()
        if not existing_user and guest_phone:
            existing_user = User.objects.filter(phone_number=guest_phone).first()

        if existing_user:
            if guest_password:
                if existing_user.check_password(guest_password):
                    CustomerService._update_missing_fields(existing_user, guest_data)
                    return existing_user, True
                elif not existing_user.has_usable_password():
                    raise OrderDomainException("این حساب فاقد رمز عبور است. لطفاً ابتدا از طریق صفحه ورود به حساب کاربری خود متصل شوید.")
                else:
                    raise OrderDomainException("رمز عبور وارد شده اشتباه است. لطفاً رمز عبور صحیح حساب خود را وارد کنید.")
            else:
                auth_mode = getattr(settings, 'AUTH_MODE', 'OTP')
                if auth_mode == 'EMAIL':
                    raise OrderDomainException("حسابی با این ایمیل در سیستم وجود دارد. لطفاً جهت تکمیل خرید، رمز عبور خود را وارد نمایید.")
                else:
                    raise OrderDomainException("حسابی با این شماره موبایل در سیستم وجود دارد. لطفاً ابتدا از طریق صفحه ورود به حساب کاربری خود متصل شوید.")

        defaults = {
            'first_name': str(guest_data.get('first_name') or '').strip(),
            'last_name': str(guest_data.get('last_name') or '').strip(),
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
        update_fields = []
        mapping = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'phone_number': 'phone'
        }
        
        for user_field, guest_field in mapping.items():
            if hasattr(user, user_field) and not getattr(user, user_field):
                guest_value = str(guest_data.get(guest_field) or '').strip()
                if guest_value:
                    setattr(user, user_field, guest_value)
                    update_fields.append(user_field)
                    
        if update_fields:
            user.save(update_fields=update_fields)