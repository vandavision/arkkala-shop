from shop.infrastructure.repositories.product import DjangoProductRepository
from shop.infrastructure.repositories.interaction import DjangoInteractionRepository
from shop.infrastructure.repositories.outbox import DjangoOutboxRepository
from shop.infrastructure.messaging.publisher import OutboxDomainEventPublisher

from shop.application.commands.create_comment import CreateCommentCommand
from shop.application.commands.create_question import CreateQuestionCommand
from shop.application.commands.increment_view_count import IncrementViewCountCommand
from shop.application.commands.toggle_favorite import ToggleFavoriteCommand
from shop.application.commands.create_product import CreateProductCommand
from shop.application.queries.get_max_price import GetMaxPriceQuery
from shop.application.queries.get_optimized_products import GetOptimizedProductsQuery
from shop.application.queries.get_user_comments import GetUserCommentsQuery

def get_product_repository() -> DjangoProductRepository:
    """Provides product repository implementation."""
    return DjangoProductRepository()

def get_interaction_repository() -> DjangoInteractionRepository:
    """Provides interaction repository implementation."""
    return DjangoInteractionRepository()

def get_outbox_repository() -> DjangoOutboxRepository:
    """Provides outbox repository implementation."""
    return DjangoOutboxRepository()

def get_event_bus() -> OutboxDomainEventPublisher:
    """Provides event bus implementation."""
    return OutboxDomainEventPublisher(outbox_repo=get_outbox_repository())


def get_create_comment_command() -> CreateCommentCommand:
    """Resolves CreateCommentCommand dependencies."""
    return CreateCommentCommand(
        product_repo=get_product_repository(),
        interaction_repo=get_interaction_repository(),
        event_bus=get_event_bus()
    )

def get_create_question_command() -> CreateQuestionCommand:
    """Resolves CreateQuestionCommand dependencies."""
    return CreateQuestionCommand(
        product_repo=get_product_repository(),
        interaction_repo=get_interaction_repository(),
        event_bus=get_event_bus()
    )

def get_increment_view_count_command() -> IncrementViewCountCommand:
    """Resolves IncrementViewCountCommand dependencies."""
    return IncrementViewCountCommand(
        product_repo=get_product_repository(),
        event_bus=get_event_bus()
    )

def get_toggle_favorite_command() -> ToggleFavoriteCommand:
    """Resolves ToggleFavoriteCommand dependencies."""
    return ToggleFavoriteCommand(
        product_repo=get_product_repository(),
        event_bus=get_event_bus()
    )

def get_create_product_command() -> CreateProductCommand:
    """Resolves CreateProductCommand dependencies."""
    return CreateProductCommand(
        product_repo=get_product_repository(),
        event_bus=get_event_bus()
    )

def get_max_price_query() -> GetMaxPriceQuery:
    """Resolves GetMaxPriceQuery dependencies."""
    return GetMaxPriceQuery(product_repo=get_product_repository())

def get_optimized_products_query() -> GetOptimizedProductsQuery:
    """Resolves GetOptimizedProductsQuery dependencies."""
    return GetOptimizedProductsQuery(product_repo=get_product_repository())

def get_user_comments_query() -> GetUserCommentsQuery:
    """Resolves GetUserCommentsQuery dependencies."""
    return GetUserCommentsQuery(interaction_repo=get_interaction_repository())