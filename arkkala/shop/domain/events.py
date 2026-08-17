from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ProductViewedEvent:
    """Event triggered when a product is viewed."""
    product_slug: str

@dataclass(frozen=True)
class ProductFavoritedEvent:
    """Event triggered when a product is favorited."""
    product_slug: str
    user_id: Any

@dataclass(frozen=True)
class ProductUnfavoritedEvent:
    """Event triggered when a product is removed from favorites."""
    product_slug: str
    user_id: Any

@dataclass(frozen=True)
class CommentCreatedEvent:
    """Event triggered when a comment is successfully created."""
    comment_uuid: str

@dataclass(frozen=True)
class QuestionCreatedEvent:
    """Event triggered when a question is successfully created."""
    question_uuid: str

@dataclass(frozen=True)
class UserViewedProductEvent:
    """Event triggered when an authenticated user views a specific product."""
    user_id: int
    product_slug: str