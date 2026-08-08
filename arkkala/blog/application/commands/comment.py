from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from blog.models.comment import Comment
from blog.repositories.post import PostRepository
from blog.repositories.comment import CommentRepository
from blog.application.dtos import CommentCreateDTO
from blog.events.publishers import DomainEventPublisher

User = get_user_model()

class CommentCommandService:
    """
    Command module executing business directives strictly isolated from Controller endpoints.
    """
    post_repo: PostRepository = PostRepository()
    comment_repo: CommentRepository = CommentRepository()

    @classmethod
    def create_comment(cls, dto: CommentCreateDTO) -> Comment:
        """
        Executes deep validations securely creating entities using designated repositories.
        """
        post = cls.post_repo.get_by_slug(dto.post_slug)
        if not post:
            raise ValueError("مقاله مورد نظر یافت نشد.")

        user = User.objects.filter(id=dto.user_id).first() if dto.user_id else None

        comment = Comment(
            post=post,
            user=user,
            body=dto.body
        )
        cls.comment_repo.save(comment)

        DomainEventPublisher.publish("CommentCreated", {"comment_uuid": str(comment.uuid)})
        return comment