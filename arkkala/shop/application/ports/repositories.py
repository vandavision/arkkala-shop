from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from django.db.models import QuerySet
from shop.models.product import Product
from shop.models.interaction import Comment, Question, UserProductHistory

class ProductRepositoryPort(ABC):
    """Business-driven port for Product persistence."""
    
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Product]:
        """Retrieves a product by its unique slug."""
        pass

    @abstractmethod
    def increment_view_count(self, slug: str) -> bool:
        """Atomically increments product view count."""
        pass

    @abstractmethod
    def toggle_favorite(self, product_slug: str, user_id: Any) -> bool:
        """Toggles user favorite status. Returns True if added, False if removed."""
        pass

    @abstractmethod
    def get_max_base_price(self) -> int:
        """Returns the maximum base price among active products."""
        pass

    @abstractmethod
    def get_active_products_optimized(self, user: Any) -> QuerySet:
        """Returns a heavily optimized queryset for listing products."""
        pass

    @abstractmethod
    def save_product(self, product: Product) -> Product:
        """Persists a new or updated product instance."""
        pass

    @abstractmethod
    def get_recommendations_for_user(self, user: Any, guest_id: Optional[str] = None) -> QuerySet:
        """Fetches personalized product recommendations based on view and purchase history."""
        pass


class InteractionRepositoryPort(ABC):
    """Business-driven port for Comments, Questions, and History."""
    
    @abstractmethod
    def save_comment(self, comment: Comment) -> Comment:
        """Persists a new comment."""
        pass

    @abstractmethod
    def save_question(self, question: Question) -> Question:
        """Persists a new question."""
        pass

    @abstractmethod
    def get_user_comments(self, user: Any) -> QuerySet:
        """Retrieves all comments authored by a specific user."""
        pass

    @abstractmethod
    def save_user_product_history(self, product: Product, user: Any = None, guest_id: Optional[str] = None) -> UserProductHistory:
        """Records or updates a user's or guest's view of a specific product."""
        pass


class OutboxRepositoryPort(ABC):
    """Business-driven port for Transactional Outbox Events."""
    
    @abstractmethod
    def save_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Persists the event payload for asynchronous processing."""
        pass