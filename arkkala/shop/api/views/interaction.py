from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from shop.api.serializers.outputs.interaction import UserCommentSerializer

class CommentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Secured User Dashboard ViewSet. 
    Strictly isolated: Users can ONLY ever see their own personal comments.
    """
    serializer_class = UserCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Security Enforcement: Delegates fetching logic to Application layer to prevent leaks."""
        import shop.dependencies as deps
        query = deps.get_user_comments_query()
        return query.execute(self.request.user)

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Paginates the resolved user comments safely."""
        qs = self.filter_queryset(self.get_queryset())
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            return paginator.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(qs, many=True).data)