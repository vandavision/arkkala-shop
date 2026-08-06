from typing import Any
from django.db import transaction
from users.models.address import UserAddress
from users.repositories.base import BaseRepository

class AddressRepository(BaseRepository[UserAddress]):
    """
    Data abstraction layer for Address management.
    """
    def __init__(self) -> None:
        """
        Initializes the Address repository.
        """
        super().__init__(UserAddress)

    def set_default_address(self, user_id: Any, address_uuid: Any) -> None:
        """
        Atomically switches the default address state to prevent multiple default addresses.
        """
        with transaction.atomic():
            self.model.objects.filter(user_id=user_id).update(is_default=False)
            self.model.objects.filter(user_id=user_id, uuid=address_uuid).update(is_default=True)