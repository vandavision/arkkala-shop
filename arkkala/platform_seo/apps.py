from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PlatformSeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "platform_seo"
    verbose_name = _("Search Engine Optimization")
