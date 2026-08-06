from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from shop.models.interaction import Comment
from shop.serializers.interaction import UserCommentSerializer

class CommentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Secured User Dashboard ViewSet. 
    Strictly isolated: Users can ONLY ever see their own personal comments.
    """
    serializer_class = UserCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Security Enforcement: No generic `.all()` leak. User isolation applied at DB level.
        """
        return Comment.objects.filter(user=self.request.user).select_related('product').order_by('-created_at')

    def list(self, request: Request, *args, **kwargs) -> Response:
        qs = self.filter_queryset(self.get_queryset())
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            return paginator.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(qs, many=True).data)