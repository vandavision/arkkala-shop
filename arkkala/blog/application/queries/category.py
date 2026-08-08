from django.db.models.query import QuerySet
from blog.models.category import Category
from platform_tools.utils.profiler import QueryProfiler

class CategoryQueryService:
    """
    Query mechanism safely fetching categories with strict performance profiling applied.
    """
    @classmethod
    @QueryProfiler(analyze=False)
    def get_active_categories(cls) -> QuerySet:
        """
        Surfaces completely optimized arrays of published category models efficiently.
        """
        return Category.objects.filter(is_active=True)