from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class UsersConfig(AppConfig):
    """
    Standardizes app execution internally correctly setup via baseline logic.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('مدیریت کاربران')