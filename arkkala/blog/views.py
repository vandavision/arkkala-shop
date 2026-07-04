"""
API Views for Blog App.
"""
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend

from .models import Post, Category
from .serializers import PostListSerializer, PostDetailSerializer, BlogCategorySerializer
from .services import PostService


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for retrieving blog categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = BlogCategorySerializer
    pagination_class = None


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving and filtering blog posts.
    """
    queryset = Post.objects.filter(is_published=True).select_related('category', 'author').prefetch_related('tags')
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'tags__slug']
    search_fields = ['title', 'short_description', 'body']
    ordering_fields = ['view_count', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Override retrieve to increment view count using Service Layer."""
        instance: Post = self.get_object()
        PostService.increment_view_count(post=instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request: Request, pk=None) -> Response:
        """Action for users to submit comments on a post."""
        try:
            post: Post = self.get_object()
            body: str = request.data.get('body')
            user = request.user if request.user.is_authenticated else None
            
            if not body:
                raise ValueError("متن نظر نمی‌تواند خالی باشد.")
                
            PostService.add_comment(
                post=post,
                user=user,
                body=body
            )
            return Response(
                {"message": "دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود."}, 
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "خطایی در ثبت نظر رخ داد."}, status=status.HTTP_400_BAD_REQUEST)