# arkkala/blog/views/post.py
from django.db.models import Prefetch, QuerySet
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from blog.models.post import Post
from blog.models.comment import Comment
from blog.serializers.post import PostListSerializer, PostDetailSerializer, CommentSubmissionSerializer
from blog.services.post import PostService
from blog.services.comment import CommentService

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for Blog Posts."""
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'tags__slug']
    search_fields = ['title', 'short_description', 'body']
    ordering_fields = ['view_count', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet:
        """Returns the optimized queryset for posts utilizing prefetch_related for Comments."""
        return Post.objects.filter(is_published=True).select_related(
            'category', 'author'
        ).prefetch_related(
            'tags',
            Prefetch('comments', queryset=Comment.objects.filter(is_approved=True), to_attr='approved_comments')
        )

    def get_serializer_class(self):
        """Dynamically assigns serializer based on current action."""
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Retrieves a single post and increments its view count dynamically."""
        instance: Post = self.get_object()
        PostService.increment_view_count(post=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=CommentSubmissionSerializer)
    def add_comment(self, request: Request, slug: str = None) -> Response:
        """Creates a new comment for a specific post instance."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            post: Post = self.get_object()
            user = request.user if request.user.is_authenticated else None
            
            CommentService.create_comment(
                post=post,
                body=serializer.validated_data['body'],
                user=user
            )
            
            return Response(
                {"message": "دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود."}, 
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)