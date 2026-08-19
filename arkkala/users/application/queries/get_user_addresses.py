from django.db.models import QuerySet
from users.application.ports.repositories import AddressRepositoryPort
from typing import Any

class GetUserAddressesQuery:
    """
    Read operation decoupling direct repository scans properly mapped.
    """
    def __init__(self, address_repo: AddressRepositoryPort) -> None:
        self.address_repo = address_repo

    def execute(self, user: Any) -> QuerySet:
        """
        Fetches operational constraints securely maintaining tenant isolations flawlessly.
        """
        return self.address_repo.get_user_addresses(user)