from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny

from home.dependencies import contact_repository
from home.application.dto.commands import SubmitContactMessageDTO
from home.application.commands.submit_contact_message import SubmitContactMessageCommand
from home.api.serializers.inputs.contact import ContactMessageInputSerializer

class ContactMessageAPIView(APIView):
    """
    Thin API View for receiving contact messages from frontend.
    """
    permission_classes: list = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ContactMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dto = SubmitContactMessageDTO(**serializer.validated_data)
        command = SubmitContactMessageCommand(repository=contact_repository)
        command.execute(dto)
        
        return Response(
            {"message": "پیام شما با موفقیت دریافت شد."},
            status=status.HTTP_201_CREATED
        )