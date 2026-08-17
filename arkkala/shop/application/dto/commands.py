from dataclasses import dataclass
from typing import Optional, Any

@dataclass(frozen=True)
class CreateCommentCommandDTO:
    """Data Transfer Object for executing Comment creation."""
    product_slug: str
    body: str
    rating: int
    user_id: Optional[int] = None

@dataclass(frozen=True)
class CreateQuestionCommandDTO:
    """Data Transfer Object for executing Question creation."""
    product_slug: str
    body: str
    user_id: Optional[int] = None
    guest_name: Optional[str] = None

@dataclass(frozen=True)
class CreateProductCommandDTO:
    """Data Transfer Object encapsulating product creation logic."""
    title: str
    slug: str
    description: str
    base_price: int
    category_id: Optional[Any] = None
    brand_id: Optional[Any] = None
    is_wholesale: bool = False
    wholesale_min_quantity: int = 10
    wholesale_base_price: Optional[int] = None

@dataclass(frozen=True)
class TrackProductViewDTO:
    """Data Transfer Object for recording user and guest product view."""
    product_slug: str
    user_id: Optional[int] = None
    guest_id: Optional[str] = None