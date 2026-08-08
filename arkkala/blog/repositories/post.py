from django.db.models import F
from blog.models.post import Post
from blog.repositories.base import BaseRepository

class PostRepository(BaseRepository[Post]):
    """
    Data access layer for Post entities isolating ORM constraints seamlessly.
    """
    def __init__(self) -> None:
        """
        Injects Post model into base operational context securely.
        """
        super().__init__(Post)

    def increment_view_count(self, slug: str) -> bool:
        """
        Atomically increments view counts eliminating Lost Update failures natively.
        """
        updated_count: int = self.model.objects.filter(slug=slug).update(view_count=F('view_count') + 1)
        return updated_count > 0