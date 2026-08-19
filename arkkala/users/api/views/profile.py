from typing import Any
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model

from users.api.serializers.outputs.profile import UserProfileOutputSerializer, UserAddressOutputSerializer
from users.api.serializers.inputs.profile import UserAddressInputSerializer
from users.application.dto.commands import SetDefaultAddressDTO
from users.dependencies import set_default_address_command, get_user_addresses_query

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        return UserProfileOutputSerializer

    @extend_schema(summary="Get/Update User Profile")
    def get_object(self) -> User:
        return self.request.user

class UserAddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserAddressInputSerializer
        return UserAddressOutputSerializer

    def get_queryset(self) -> Any:
        return get_user_addresses_query.execute(self.request.user)

    def perform_create(self, serializer: Any) -> None:
        serializer.save(user=self.request.user)

    @extend_schema(summary="Set Address as Default")
    @action(detail=True, methods=['post'])
    def set_default(self, request: Request, uuid: str | None = None) -> Response:
        dto = SetDefaultAddressDTO(user_id=request.user.id, address_uuid=uuid)
        set_default_address_command.execute(dto)
        return Response({"message": "آدرس پیش‌فرض با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)