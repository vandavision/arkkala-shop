from typing import Any
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema

from users.serializers.auth import (
    EmailRegisterSerializer, EmailLoginSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    OTPSendSerializer, OTPVerifySerializer
)
from users.application.commands.auth import AuthCommandService
from users.application.dtos import (
    OTPSendDTO, OTPVerifyDTO, EmailRegisterDTO, 
    EmailLoginDTO, PasswordResetConfirmDTO
)

def get_client_ip(request: Request) -> str:
    """
    Extracts HTTP protocol variables extracting optimal proxy networks securely.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR') or '127.0.0.1'

class AuthConfigView(APIView):
    """
    Echoes fundamental setup rules for user interactions statically.
    """
    permission_classes = [AllowAny]

    @extend_schema(summary="Get Active Authentication Mode")
    def get(self, request: Request) -> Response:
        mode: str = getattr(settings, 'AUTH_MODE', 'OTP')
        return Response({"mode": mode}, status=status.HTTP_200_OK)

class OTPSendView(APIView):
    """
    Handles request mapping securely for data endpoints structurally.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=OTPSendSerializer, summary="Send OTP SMS")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'OTP':
            return Response({"error": "احراز هویت پیامکی در سیستم غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = OTPSendDTO(
            identifier=serializer.validated_data['phone_number'],
            ip_address=get_client_ip(request),
            is_email_reset=False
        )

        try:
            AuthCommandService.send_otp(dto)
            return Response({"message": "کد تایید با موفقیت ارسال شد."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OTPVerifyView(APIView):
    """
    Relays structurally secured execution endpoints natively.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=OTPVerifySerializer, summary="Verify OTP and Login")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'OTP':
            return Response({"error": "احراز هویت پیامکی در سیستم غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = OTPVerifyDTO(
            identifier=serializer.validated_data['phone_number'],
            code=serializer.validated_data['code'],
            guest_id=request.headers.get('X-Guest-ID'),
            client_ip=get_client_ip(request)
        )

        try:
            result: dict = AuthCommandService.verify_otp_and_login(dto)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EmailRegisterView(APIView):
    """
    Isolates external layer bindings avoiding tight couplings.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=EmailRegisterSerializer, summary="Register using Email")
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ثبت‌نام ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EmailRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = EmailRegisterDTO(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            guest_id=request.headers.get('X-Guest-ID'),
            client_ip=get_client_ip(request)
        )

        try:
            AuthCommandService.register_email(dto)
            return Response({"message": "ثبت نام با موفقیت انجام شد."}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EmailLoginView(APIView):
    """
    Restricts structural payload requests strictly mapping.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=EmailLoginSerializer, summary="Login using Email")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ورود ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = EmailLoginDTO(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            guest_id=request.headers.get('X-Guest-ID'),
            client_ip=get_client_ip(request)
        )

        try:
            result: dict = AuthCommandService.login_email(dto)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    """
    Bridges application boundaries effectively.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=PasswordResetRequestSerializer, summary="Request Email Password Reset")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "این امکان فقط در حالت ایمیل فعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = OTPSendDTO(
            identifier=serializer.validated_data['email'],
            ip_address=get_client_ip(request),
            is_email_reset=True
        )

        try:
            AuthCommandService.send_otp(dto)
            return Response({"message": "کد بازیابی رمز عبور به ایمیل شما ارسال شد."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """
    Concludes modification requests structurally perfectly.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=PasswordResetConfirmSerializer, summary="Confirm Email Password Reset")
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "این امکان فقط در حالت ایمیل فعال است."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dto = PasswordResetConfirmDTO(
            email=serializer.validated_data['email'],
            code=serializer.validated_data['code'],
            new_password=serializer.validated_data['new_password']
        )

        try:
            AuthCommandService.verify_reset_code_and_set_password(dto)
            return Response({"message": "رمز عبور با موفقیت تغییر کرد. اکنون وارد شوید."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)