from typing import Any, Optional, Callable
from django.core.cache import cache

class CacheStrategy:
    """
    Base Service for implementing robust caching strategies across the application.
    """
    def __init__(self, prefix: str, default_timeout: int = 86400) -> None:
        self.prefix: str = prefix
        self.default_timeout: int = default_timeout

    def _generate_key(self, key: str) -> str:
        """
        Generates a namespace-isolated cache key.
        """
        return f"{self.prefix}:{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves data from cache.
        """
        return cache.get(self._generate_key(key))

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Stores data into cache.
        """
        cache.set(self._generate_key(key), value, timeout or self.default_timeout)

    def invalidate(self, key: str) -> None:
        """
        Deletes specific key from cache.
        """
        cache.delete(self._generate_key(key))

    def get_or_set(self, key: str, query_func: Callable[[], Any], timeout: Optional[int] = None) -> Any:
        """
        Retrieves from cache if exists, otherwise executes the callable to fetch and store.
        """
        cached_data: Optional[Any] = self.get(key)
        if cached_data is not None:
            return cached_data
        data: Any = query_func()
        self.set(key, data, timeout)
        return data