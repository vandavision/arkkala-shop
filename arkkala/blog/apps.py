from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'blog'
    verbose_name: str = 'مدیریت وبلاگ'

    def ready(self) -> None:
        import blog.signals