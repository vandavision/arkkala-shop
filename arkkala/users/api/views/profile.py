from typing import Any
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model

from users.api.serializers.outputs.profile import UserProfileOutputSerializer, UserAddressOutputSerializer
from users.api.serializers.inputs.profile import UserAddressInputSerializer, UserProfileInputSerializer
from users.application.dto.commands import SetDefaultAddressDTO
from users.dependencies import set_default_address_command, get_user_addresses_query

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Provides secure interface for user detail resolutions mapping cleanly.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> Any:
        """
        Selects accurate serialization format resolving correctly.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileInputSerializer
        return UserProfileOutputSerializer

    @extend_schema(summary="Get/Update User Profile")
    def get_object(self) -> Any:
        """
        Returns the active user context safely.
        """
        return self.request.user

class UserAddressViewSet(viewsets.ModelViewSet):
    """
    Resolves complex CRUD iterations matching explicit structures effectively.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_serializer_class(self) -> Any:
        """
        Determines appropriate serializers based on action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return UserAddressInputSerializer
        return UserAddressOutputSerializer

    def get_queryset(self) -> Any:
        """
        Retrieves user-scoped addresses.
        """
        return get_user_addresses_query.execute(self.request.user)

    def perform_create(self, serializer: Any) -> None:
        """
        Binds context explicitly bypassing arbitrary assignments.
        """
        serializer.save(user=self.request.user)

    @extend_schema(summary="Set Address as Default")
    @action(detail=True, methods=['post'])
    def set_default(self, request: Request, uuid: str | None = None) -> Response:
        """
        Modifies routing hierarchy correctly updating instances reliably.
        """
        dto = SetDefaultAddressDTO(user_id=request.user.id, address_uuid=uuid)
        set_default_address_command.execute(dto)
        return Response({"message": "آدرس پیش‌فرض با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)