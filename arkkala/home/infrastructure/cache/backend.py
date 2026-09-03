from typing import Dict, Any, Optional
from django.core.cache import cache
from home.application.ports.cache import HomeCache
from home.infrastructure.cache.keys import CacheKeys

class HomeCacheBackend(HomeCache):
    """
    Django implementation of the HomeCache port.
    """
    def get_home_page_data(self) -> Optional[Dict[str, Any]]:
        return cache.get(CacheKeys.home_page_aggregated_data())

    def set_home_page_data(self, data: Dict[str, Any]) -> None:
        cache.set(CacheKeys.home_page_aggregated_data(), data, timeout=600)

    def clear_home_page_data(self) -> None:
        cache.delete(CacheKeys.home_page_aggregated_data())