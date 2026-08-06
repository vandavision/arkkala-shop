from typing import Any
from django.db.models.query import QuerySet
from users.models.address import UserAddress

class UserQueryService:
    """
    CQRS Read Operations. Strictly no database modifications here.
    """
    @classmethod
    def get_user_addresses(cls, user: Any) -> QuerySet:
        """
        Retrieves an isolated QuerySet of addresses exclusively belonging to the user.
        """
        return UserAddress.objects.filter(user=user)