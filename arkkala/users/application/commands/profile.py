from typing import Any
from users.repositories.address import AddressRepository
from users.events.publishers import DomainEventPublisher

class ProfileCommandService:
    """
    CQRS Write Operations for User Profile domains.
    """
    address_repo = AddressRepository()

    @classmethod
    def set_default_address(cls, user_id: Any, address_uuid: Any) -> None:
        """
        Safely invokes repository to swap defaults and publishes domain event.
        """
        cls.address_repo.set_default_address(user_id, address_uuid)
        DomainEventPublisher.publish("UserAddressDefaultChanged", {"user_id": user_id, "address_uuid": str(address_uuid)})