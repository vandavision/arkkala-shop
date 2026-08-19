from django.db import transaction
from users.application.dto.commands import SetDefaultAddressDTO
from users.application.ports.repositories import AddressRepositoryPort
from users.domain.events import DomainEventPublisher

class SetDefaultAddressCommand:
    """
    Use case managing priority updates preventing concurrency races thoroughly.
    """
    def __init__(self, address_repo: AddressRepositoryPort) -> None:
        self.address_repo = address_repo

    def execute(self, dto: SetDefaultAddressDTO) -> None:
        """
        Guarantees isolation mapping database manipulations purely.
        """
        with transaction.atomic():
            self.address_repo.set_default_address(dto.user_id, dto.address_uuid)
            
        DomainEventPublisher.publish("UserAddressDefaultChanged", {"user_id": dto.user_id, "address_uuid": dto.address_uuid})