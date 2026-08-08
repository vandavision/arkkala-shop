from typing import Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from blog.api.serializers.outputs.post import PostListSerializer, PostDetailSerializer
from blog.api.serializers.inputs.comment import CommentSubmissionSerializer
from blog.dependencies import get_post_repository, get_comment_repository, get_event_publisher
from blog.application.queries.list_optimized_posts import ListOptimizedPostsUseCase
from blog.application.commands.increment_view_count import IncrementPostViewCountUseCase
from blog.application.commands.create_comment import CreateCommentUseCase
from blog.application.dto.commands import CreateCommentCommandDTO
from blog.api.pagination import BlogPagination

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field: str = 'slug'
    filter_backends: list = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: list = ['category__slug', 'tags__slug']
    search_fields: list = ['title', 'short_description', 'body']
    ordering_fields: list = ['view_count', 'created_at']
    ordering: list = ['-created_at']
    pagination_class = BlogPagination

    @extend_schema(summary="List Optimized Posts")
    def get_queryset(self) -> QuerySet:
        use_case = ListOptimizedPostsUseCase(get_post_repository())
        return use_case.execute()

    def get_serializer_class(self) -> Any:
        if self.action == 'list':
            return PostListSerializer
        if self.action == 'add_comment':
            return CommentSubmissionSerializer
        return PostDetailSerializer

    @extend_schema(summary="Retrieve Post Detail")
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        
        use_case = IncrementPostViewCountUseCase(get_post_repository(), get_event_publisher())
        use_case.execute(instance.slug)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(request=CommentSubmissionSerializer, summary="Submit Comment")
    @action(detail=True, methods=['post'], serializer_class=CommentSubmissionSerializer)
    def add_comment(self, request: Request, slug: str | None = None) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dto = CreateCommentCommandDTO(
            post_slug=instance.slug,
            body=serializer.validated_data['body'],
            user_id=request.user.id if request.user.is_authenticated else None
        )
        
        use_case = CreateCommentUseCase(get_post_repository(), get_comment_repository(), get_event_publisher())
        
        try:
            use_case.execute(dto)
            return Response(
                {"message": "دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود."}, 
                status=status.HTTP_201_CREATED
            )
        except (ValueError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)