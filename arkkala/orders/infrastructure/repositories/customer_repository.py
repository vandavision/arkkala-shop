from typing import Optional, Tuple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from orders.application.ports.repositories import CustomerRepository
from orders.services.customer import CustomerService

User = get_user_model()


class DjangoCustomerRepository(CustomerRepository):
    """Django ORM implementation for cross-domain user resolution."""

    def resolve_checkout_user(self, user_id: Optional[int], guest_data: dict) -> Tuple[Optional[AbstractUser], bool]:
        user = User.objects.filter(id=user_id).first() if user_id else None
        return CustomerService.resolve_checkout_user(user, guest_data)