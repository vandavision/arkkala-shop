from django.db.models.query import QuerySet
from django.db.models import Prefetch
from blog.models.post import Post
from blog.models.comment import Comment
from platform_tools.services.cache import CacheStrategy
from platform_tools.utils.profiler import QueryProfiler

class PostQueryService:
    """
    Query module managing data graph extraction removing N+1 performance bottlenecks entirely.
    """
    cache_strategy: CacheStrategy = CacheStrategy(prefix="blog:post")

    @classmethod
    @QueryProfiler(analyze=False)
    def get_optimized_posts(cls) -> QuerySet:
        """
        Resolves relational tree completely providing views fully integrated datasets seamlessly.
        """
        return Post.objects.filter(is_published=True).select_related(
            'category', 'author'
        ).prefetch_related(
            'tags',
            Prefetch(
                'comments', 
                queryset=Comment.objects.filter(is_approved=True), 
                to_attr='approved_comments'
            )
        )