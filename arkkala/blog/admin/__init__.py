# arkkala/blog/admin/__init__.py
from .category import CategoryAdmin
from .tag import TagAdmin
from .post import PostAdmin
from .comment import CommentAdmin

__all__ = ['CategoryAdmin', 'TagAdmin', 'PostAdmin', 'CommentAdmin']