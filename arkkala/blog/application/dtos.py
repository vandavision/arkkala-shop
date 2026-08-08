from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CommentCreateDTO:
    """
    Immutable transport structure guaranteeing robust payload integrity for comments.
    """
    post_slug: str
    body: str
    user_id: Optional[int] = None