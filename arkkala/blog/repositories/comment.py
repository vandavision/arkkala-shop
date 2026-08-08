from blog.models.comment import Comment
from blog.repositories.base import BaseRepository

class CommentRepository(BaseRepository[Comment]):
    """
    Data access layer exclusively orchestrating Comment persistence behaviors.
    """
    def __init__(self) -> None:
        """
        Instantiates specific entity boundary mapping.
        """
        super().__init__(Comment)