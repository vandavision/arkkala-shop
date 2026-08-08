from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BlogConfig(AppConfig):
    """
    Configuration for the Blog application with signal auto-registration.
    """
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'blog'
    verbose_name: str = _('مدیریت وبلاگ')

    def ready(self) -> None:
        """
        Imports and registers signals upon application readiness preventing stale cache.
        """
        import blog.signals