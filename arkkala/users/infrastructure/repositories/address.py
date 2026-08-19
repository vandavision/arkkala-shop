from typing import Any
from django.db.models import QuerySet
from users.models.address import UserAddress
from users.application.ports.repositories import AddressRepositoryPort

class AddressRepositoryImpl(AddressRepositoryPort):
    """
    Concrete implementation resolving relational scans dynamically seamlessly.
    """
    def get_user_addresses(self, user: Any) -> QuerySet:
        return UserAddress.objects.filter(user=user)

    def set_default_address(self, user_id: Any, address_uuid: Any) -> None:
        UserAddress.objects.filter(user_id=user_id).update(is_default=False)
        UserAddress.objects.filter(user_id=user_id, uuid=address_uuid).update(is_default=True)