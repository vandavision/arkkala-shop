from typing import TypeVar, Generic, Type, Optional, Any
from django.db.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """
    Generic Repository Pattern implementation abstracting direct ORM usage.
    """
    def __init__(self, model: Type[T]) -> None:
        """
        Initializes repository with a specific model type.
        """
        self.model = model

    def get_by_uuid(self, uuid: Any) -> Optional[T]:
        """
        Retrieves instance via UUID safely.
        """
        try:
            return self.model.objects.get(uuid=uuid)
        except self.model.DoesNotExist:
            return None

    def save(self, instance: T) -> T:
        """
        Enforces validation before writing to DB.
        """
        instance.full_clean()
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        """
        Deletes the instance from DB.
        """
        instance.delete()