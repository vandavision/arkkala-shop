from django.db.models.signals import post_save, post_delete
from home.models import Story, Slider, Banner, StoreReview, SiteSetting, FAQ, AboutPage
from shop.models import Product, Brand, Category as ShopCategory
from blog.models import Post
from home.dependencies import home_cache_backend

MODELS_TO_WATCH = [
    Story, Slider, Banner, StoreReview, SiteSetting, FAQ, AboutPage,
    Product, Brand, ShopCategory, Post
]

def invalidate_home_cache(sender, **kwargs) -> None:
    """
    Clears the home page cache whenever related models are updated or deleted.
    """
    home_cache_backend.clear_home_page_data()

for model in MODELS_TO_WATCH:
    post_save.connect(invalidate_home_cache, sender=model)
    post_delete.connect(invalidate_home_cache, sender=model)