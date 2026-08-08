from django.db.models import QuerySet
from blog.application.ports.repositories import PostRepositoryPort

class ListOptimizedPostsUseCase:
    def __init__(self, post_repo: PostRepositoryPort) -> None:
        self.post_repo = post_repo

    def execute(self) -> QuerySet:
        return self.post_repo.get_published_posts_optimized()