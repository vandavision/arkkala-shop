from django.contrib.auth import get_user_model
from django.db import transaction
from blog.models.comment import Comment
from blog.application.dto.commands import CreateCommentCommandDTO
from blog.application.ports.repositories import PostRepositoryPort, CommentRepositoryPort
from blog.application.ports.event_bus import EventBusPort
from blog.domain.events import CommentCreatedEvent

User = get_user_model()

class CreateCommentUseCase:
    def __init__(self, post_repo: PostRepositoryPort, comment_repo: CommentRepositoryPort, event_bus: EventBusPort) -> None:
        self.post_repo = post_repo
        self.comment_repo = comment_repo
        self.event_bus = event_bus

    @transaction.atomic
    def execute(self, dto: CreateCommentCommandDTO) -> Comment:
        post = self.post_repo.get_by_slug(dto.post_slug)
        if not post:
            raise ValueError("مقاله مورد نظر یافت نشد.")

        user = User.objects.filter(id=dto.user_id).first() if dto.user_id else None

        comment = Comment(
            post=post,
            user=user,
            body=dto.body
        )
        comment.full_clean()
        self.comment_repo.save_comment(comment)

        event = CommentCreatedEvent(comment_uuid=str(comment.uuid))
        transaction.on_commit(lambda: self.event_bus.publish(event))
        
        return comment