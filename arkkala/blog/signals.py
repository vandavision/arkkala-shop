from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from blog.models.post import Post
from blog.models.category import Category
from blog.models.comment import Comment
from platform_tools.services.cache import CacheStrategy

cache_strategy = CacheStrategy(prefix="blog:post")

@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Post)
@receiver([post_save, post_delete], sender=Comment)
def invalidate_blog_caches(sender, instance, **kwargs) -> None:
    cache_strategy.invalidate("list")
    if hasattr(instance, 'pk'):
        cache_strategy.invalidate(str(instance.pk))
    
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern("blog:*")