from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class HomeConfig(AppConfig):
    """
    App configuration for the Home application.
    """
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'home'
    verbose_name: str = _('خانه')