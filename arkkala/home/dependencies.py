from home.infrastructure.repositories.contact_repository import DjangoContactRepository
from home.infrastructure.readers.home_page_reader import DjangoHomePageReader
from home.infrastructure.cache.backend import HomeCacheBackend

contact_repository: DjangoContactRepository = DjangoContactRepository()
home_page_reader: DjangoHomePageReader = DjangoHomePageReader()
home_cache_backend: HomeCacheBackend = HomeCacheBackend()