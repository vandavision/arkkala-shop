# shop/views/interaction.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from shop.models.interaction import Comment
from shop.serializers.interaction import UserCommentSerializer


class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = UserCommentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_comments(self, request: Request) -> Response:
        qs = self.get_queryset().filter(user=request.user).select_related('product').order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(qs, request)
        
        if page is not None:
            return paginator.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(qs, many=True).data)