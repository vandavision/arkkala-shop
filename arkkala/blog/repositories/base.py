from typing import TypeVar, Generic, Type, Optional, Any
from django.db.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """
    Abstract repository enforcing database decoupling and rigid validation state correctly.
    """
    def __init__(self, model: Type[T]) -> None:
        """
        Initializes base repository with the specific model class safely.
        """
        self.model = model

    def get_by_uuid(self, uuid: Any) -> Optional[T]:
        """
        Retrieves instance via UUID handling native exceptions safely.
        """
        try:
            return self.model.objects.get(uuid=uuid)
        except self.model.DoesNotExist:
            return None

    def get_by_slug(self, slug: str) -> Optional[T]:
        """
        Retrieves instance via URL-friendly slug catching unmapped states.
        """
        try:
            return self.model.objects.get(slug=slug)
        except self.model.DoesNotExist:
            return None

    def save(self, instance: T) -> T:
        """
        Enforces validation before writing directly executing clean functions dynamically.
        """
        instance.full_clean()
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        """
        Safely removes instance from database execution context.
        """
        instance.delete()