from blog.repositories.post import PostRepository
from blog.events.publishers import DomainEventPublisher

class PostCommandService:
    """
    Command dispatcher enforcing write modifications dynamically across Post architecture.
    """
    repository: PostRepository = PostRepository()

    @classmethod
    def increment_view_count(cls, post_slug: str) -> None:
        """
        Coordinates database abstraction and event broadcast seamlessly avoiding logic collisions.
        """
        is_updated: bool = cls.repository.increment_view_count(post_slug)
        if is_updated:
            DomainEventPublisher.publish("PostViewed", {"post_slug": post_slug})