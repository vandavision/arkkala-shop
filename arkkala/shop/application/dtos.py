from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class InteractionCreateDTO:
    """
    Data Transfer Object for creating an interaction.
    """
    product_slug: str
    body: str
    user_id: Optional[int] = None
    rating: int = 5
    name: Optional[str] = None