from blog.models.comment import Comment
from blog.application.ports.repositories import CommentRepositoryPort

class DjangoCommentRepository(CommentRepositoryPort):
    def save_comment(self, comment: Comment) -> Comment:
        comment.save()
        return comment