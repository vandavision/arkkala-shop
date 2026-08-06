from typing import TypeVar, Generic, Type, Optional, Any
from django.db.models import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    """
    Generic Repository Pattern implementation.
    """
    def __init__(self, model: Type[T]) -> None:
        self.model = model

    def get_by_uuid(self, uuid: Any) -> Optional[T]:
        try:
            return self.model.objects.get(uuid=uuid)
        except self.model.DoesNotExist:
            return None

    def get_by_slug(self, slug: str) -> Optional[T]:
        try:
            return self.model.objects.get(slug=slug)
        except self.model.DoesNotExist:
            return None

    def save(self, instance: T) -> T:
        instance.full_clean()
        instance.save()
        return instance

    def delete(self, instance: T) -> None:
        instance.delete()