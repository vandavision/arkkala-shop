from blog.application.ports.repositories import PostRepositoryPort
from blog.application.ports.event_bus import EventBusPort
from blog.domain.events import PostViewedEvent

class IncrementPostViewCountUseCase:
    def __init__(self, post_repo: PostRepositoryPort, event_bus: EventBusPort) -> None:
        self.post_repo = post_repo
        self.event_bus = event_bus

    def execute(self, post_slug: str) -> None:
        is_updated = self.post_repo.increment_view_count(post_slug)
        if is_updated:
            self.event_bus.publish(PostViewedEvent(post_slug=post_slug))