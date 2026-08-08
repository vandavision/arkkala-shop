from blog.infrastructure.repositories.post_repository import DjangoPostRepository
from blog.infrastructure.repositories.comment_repository import DjangoCommentRepository
from blog.infrastructure.repositories.category_repository import DjangoCategoryRepository
from blog.infrastructure.messaging.publisher import DjangoEventPublisher

def get_post_repository() -> DjangoPostRepository:
    return DjangoPostRepository()

def get_comment_repository() -> DjangoCommentRepository:
    return DjangoCommentRepository()

def get_category_repository() -> DjangoCategoryRepository:
    return DjangoCategoryRepository()

def get_event_publisher() -> DjangoEventPublisher:
    return DjangoEventPublisher()