from django.db.models import QuerySet
from blog.models.category import Category
from blog.application.ports.repositories import CategoryRepositoryPort
from platform_tools.utils.profiler import QueryProfiler

class DjangoCategoryRepository(CategoryRepositoryPort):
    @QueryProfiler(analyze=False)
    def get_active_categories(self) -> QuerySet:
        return Category.objects.filter(is_active=True)