from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CreateCommentCommandDTO:
    post_slug: str
    body: str
    user_id: Optional[int] = None