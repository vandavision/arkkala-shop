from django.apps import AppConfig

class ShopConfig(AppConfig):
    """Configuration for the Shop application."""
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'shop'
    verbose_name: str = 'مدیریت فروشگاه'

    def ready(self) -> None:
        """Imports signal handlers when the app is ready."""
        import shop.signals