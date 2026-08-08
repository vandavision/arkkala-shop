from django.db.models import QuerySet
from blog.application.ports.repositories import CategoryRepositoryPort

class GetActiveCategoriesUseCase:
    def __init__(self, category_repo: CategoryRepositoryPort) -> None:
        self.category_repo = category_repo

    def execute(self) -> QuerySet:
        return self.category_repo.get_active_categories()