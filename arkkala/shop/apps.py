"""
App configuration for the shop module.
"""
from django.apps import AppConfig

class ShopConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'shop'
    verbose_name: str = 'مدیریت فروشگاه'