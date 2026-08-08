from typing import Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from blog.models.post import Post
from blog.serializers.post import PostListSerializer, PostDetailSerializer, CommentSubmissionSerializer
from blog.application.queries.post import PostQueryService
from blog.application.commands.post import PostCommandService
from blog.application.commands.comment import CommentCommandService
from blog.application.dtos import CommentCreateDTO

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Thin controller architecture bridging Query and Command segregations flawlessly.
    """
    lookup_field: str = 'slug'
    filter_backends: list = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields: list = ['category__slug', 'tags__slug']
    search_fields: list = ['title', 'short_description', 'body']
    ordering_fields: list = ['view_count', 'created_at']
    ordering: list = ['-created_at']
    pagination_class = None

    @extend_schema(summary="Retrieve highly optimized lists of published posts")
    def get_queryset(self) -> QuerySet:
        """
        Consumes logic isolated completely within architectural service constraints.
        """
        return PostQueryService.get_optimized_posts()

    def get_serializer_class(self) -> Any:
        """
        Switches representational structures accurately modifying volume response logically.
        """
        if self.action == 'list':
            return PostListSerializer
        if self.action == 'add_comment':
            return CommentSubmissionSerializer
        return PostDetailSerializer

    @extend_schema(summary="Retrieve detailed post info and trigger view count atomically")
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Triggers command logic effectively completing process and streaming outputs correctly.
        """
        instance: Post = self.get_object()
        PostCommandService.increment_view_count(instance.slug)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(request=CommentSubmissionSerializer, summary="Securely submit comments bypassing ORM leaks")
    @action(detail=True, methods=['post'], serializer_class=CommentSubmissionSerializer)
    def add_comment(self, request: Request, slug: str | None = None) -> Response:
        """
        Translates raw inbound payloads generating strict Data Transfer Object mechanisms completely.
        """
        instance: Post = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            dto = CommentCreateDTO(
                post_slug=instance.slug,
                body=serializer.validated_data['body'],
                user_id=request.user.id if request.user.is_authenticated else None
            )
            CommentCommandService.create_comment(dto)
            
            return Response(
                {"message": "دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود."}, 
                status=status.HTTP_201_CREATED
            )
        except (ValueError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)