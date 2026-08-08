from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class CommentCreatedEvent:
    comment_uuid: str
    name: str = "CommentCreated"
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {"comment_uuid": self.comment_uuid}

@dataclass(frozen=True)
class PostViewedEvent:
    post_slug: str
    name: str = "PostViewed"
    
    @property
    def payload(self) -> Dict[str, Any]:
        return {"post_slug": self.post_slug}