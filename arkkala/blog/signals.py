from typing import Any
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from blog.models.post import Post
from blog.models.category import Category
from blog.models.comment import Comment
from blog.application.queries.post import PostQueryService

@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Post)
@receiver([post_save, post_delete], sender=Comment)
def invalidate_blog_caches(sender: Any, instance: Any, **kwargs: Any) -> None:
    """
    Guarantees strict cache eviction handling memory gracefully without raising backend exceptions.
    """
    PostQueryService.cache_strategy.invalidate("list")
    PostQueryService.cache_strategy.invalidate(str(instance.pk))
    
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("blog:*")
    else:
        cache.clear()