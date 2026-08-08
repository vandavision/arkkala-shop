from typing import Optional
from django.db.models import F, Prefetch, QuerySet
from blog.models.post import Post
from blog.models.comment import Comment
from blog.application.ports.repositories import PostRepositoryPort
from platform_tools.utils.profiler import QueryProfiler

class DjangoPostRepository(PostRepositoryPort):
    def get_by_slug(self, slug: str) -> Optional[Post]:
        return Post.objects.filter(slug=slug, is_published=True).first()

    def increment_view_count(self, slug: str) -> bool:
        updated_count = Post.objects.filter(slug=slug).update(view_count=F('view_count') + 1)
        return updated_count > 0

    @QueryProfiler(analyze=False)
    def get_published_posts_optimized(self) -> QuerySet:
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