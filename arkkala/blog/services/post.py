from django.db.models import F, QuerySet, Prefetch
from platform_tools.services.cache import CacheStrategy
from platform_tools.utils.profiler import QueryProfiler
from blog.models.post import Post
from blog.models.comment import Comment

class PostService:
    """
    Service layer for Post business logic, profiling, and database optimizations.
    """
    cache_strategy = CacheStrategy(prefix="blog:post")

    @classmethod
    def increment_view_count(cls, post: Post) -> None:
        """
        Increments the view count of a post atomically.
        """
        Post.objects.filter(pk=post.pk).update(view_count=F('view_count') + 1)
        post.refresh_from_db(fields=['view_count'])

    @classmethod
    @QueryProfiler(analyze=False)
    def get_optimized_posts(cls) -> QuerySet:
        """
        Returns an optimized queryset utilizing prefetch_related for Comments and Tags to resolve N+1.
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