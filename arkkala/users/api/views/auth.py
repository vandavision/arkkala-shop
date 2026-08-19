from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema

from users.api.serializers.inputs.auth import (
    EmailRegisterInputSerializer, EmailLoginInputSerializer, 
    PasswordResetRequestInputSerializer, PasswordResetConfirmInputSerializer,
    OTPSendInputSerializer, OTPVerifyInputSerializer
)
from users.api.serializers.outputs.auth import TokenOutputSerializer
from users.application.dto.commands import (
    OTPSendDTO, OTPVerifyDTO, EmailRegisterDTO, 
    EmailLoginDTO, PasswordResetConfirmDTO
)
from users.dependencies import (
    send_otp_command, verify_otp_command, register_email_command, 
    login_email_command, reset_password_command
)

def get_client_ip(request: Request) -> str:
    """
    Extracts HTTP protocol variables extracting optimal proxy networks securely avoiding manipulations implicitly.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR') or '127.0.0.1'

class AuthConfigView(APIView):
    """
    Exposes setup operational configuration definitively.
    """
    permission_classes = [AllowAny]

    @extend_schema(summary="Get Active Authentication Mode")
    def get(self, request: Request) -> Response:
        mode: str = getattr(settings, 'AUTH_MODE', 'OTP')
        return Response({"mode": mode}, status=status.HTTP_200_OK)

class OTPSendView(APIView):
    """
    Triggers generation mechanisms completely decoupled effectively.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=OTPSendInputSerializer, summary="Send OTP SMS")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'OTP':
            return Response({"error": "احراز هویت پیامکی در سیستم غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OTPSendInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = OTPSendDTO(
            identifier=serializer.validated_data['phone_number'],
            ip_address=get_client_ip(request),
            is_email_reset=False
        )
        send_otp_command.execute(dto)
        return Response({"message": "کد تایید با موفقیت ارسال شد."}, status=status.HTTP_200_OK)

class OTPVerifyView(APIView):
    """
    Implements verification mapping operations seamlessly executing rules reliably.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=OTPVerifyInputSerializer, responses=TokenOutputSerializer, summary="Verify OTP and Login")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'OTP':
            return Response({"error": "احراز هویت پیامکی در سیستم غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OTPVerifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = OTPVerifyDTO(
            identifier=serializer.validated_data['phone_number'],
            code=serializer.validated_data['code'],
            guest_id=request.headers.get('X-Guest-ID'),
            client_ip=get_client_ip(request)
        )
        
        result_dto = verify_otp_command.execute(dto)
        out_serializer = TokenOutputSerializer(result_dto)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

class EmailRegisterView(APIView):
    """
    Creates isolated entity records inherently.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=EmailRegisterInputSerializer, summary="Register using Email")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ثبت‌نام ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EmailRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = EmailRegisterDTO(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            guest_id=request.headers.get('X-Guest-ID'),
            client_ip=get_client_ip(request)
        )
        
        register_email_command.execute(dto)
        return Response({"message": "ثبت نام با موفقیت انجام شد."}, status=status.HTTP_201_CREATED)

class EmailLoginView(APIView):
    """
    Initiates standard JWT generation perfectly.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=EmailLoginInputSerializer, responses=TokenOutputSerializer, summary="Login using Email")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ورود ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EmailLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = EmailLoginDTO(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            guest_id=request.headers.get('X-Guest-ID'),
            client_ip=get_client_ip(request)
        )
        
        result_dto = login_email_command.execute(dto)
        out_serializer = TokenOutputSerializer(result_dto)
        return Response(out_serializer.data, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    """
    Activates verification constraints flawlessly handling email integrations automatically.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=PasswordResetRequestInputSerializer, summary="Request Email Password Reset")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "این امکان فقط در حالت ایمیل فعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PasswordResetRequestInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = OTPSendDTO(
            identifier=serializer.validated_data['email'],
            ip_address=get_client_ip(request),
            is_email_reset=True
        )
        
        send_otp_command.execute(dto)
        return Response({"message": "کد بازیابی رمز عبور به ایمیل شما ارسال شد."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    """
    Modifies internal structural attributes guaranteeing mapping integrity.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=PasswordResetConfirmInputSerializer, summary="Confirm Email Password Reset")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "این امکان فقط در حالت ایمیل فعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PasswordResetConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = PasswordResetConfirmDTO(
            email=serializer.validated_data['email'],
            code=serializer.validated_data['code'],
            new_password=serializer.validated_data['new_password']
        )
        
        reset_password_command.execute(dto)
        return Response({"message": "رمز عبور با موفقیت تغییر کرد. اکنون وارد شوید."}, status=status.HTTP_200_OK)