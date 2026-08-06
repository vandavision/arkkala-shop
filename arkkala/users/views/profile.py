from typing import Any
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model

from users.serializers.profile import UserProfileSerializer, UserAddressSerializer
from users.application.commands.profile import ProfileCommandService
from users.application.queries.user import UserQueryService

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Provides isolated user profile endpoints effortlessly mapping to core standard generics.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(summary="Get/Update User Profile")
    def get_object(self) -> User:
        """
        Ensures strict extraction safely locked to token owner.
        """
        return self.request.user

class UserAddressViewSet(viewsets.ModelViewSet):
    """
    Robust viewset securely wrapped to exclusively process query logic correctly.
    """
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_queryset(self) -> Any:
        """
        Forces complete isolation eliminating generic leaks.
        """
        return UserQueryService.get_user_addresses(self.request.user)

    def perform_create(self, serializer: UserAddressSerializer) -> None:
        """
        Forces entity correlation safely internally.
        """
        serializer.save(user=self.request.user)

    @extend_schema(summary="Set Address as Default")
    @action(detail=True, methods=['post'])
    def set_default(self, request: Request, uuid: str | None = None) -> Response:
        """
        Delegates atomic state update correctly.
        """
        ProfileCommandService.set_default_address(request.user.id, uuid)
        return Response({"message": "آدرس پیش‌فرض با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)