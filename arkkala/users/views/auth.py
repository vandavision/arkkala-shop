from typing import Any
from django.conf import settings
from rest_framework import status, generics
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
from users.application.dtos import OTPSendDTO, OTPVerifyDTO, EmailRegisterDTO, PasswordResetConfirmDTO


def get_client_ip(request: Request) -> str:
    """
    Securely detects exact client IP across standard headers for accurate rate limiting.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR') or '127.0.0.1'


class AuthConfigView(APIView):
    """
    Returns global application auth mode configuration seamlessly to the frontend.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(summary="Get Active Authentication Mode")
    def get(self, request: Request) -> Response:
        """
        Retrieves auth mode standard.
        """
        mode: str = getattr(settings, 'AUTH_MODE', 'OTP')
        return Response({"mode": mode}, status=status.HTTP_200_OK)


class OTPSendView(APIView):
    """
    Thin layer strictly executing data gathering and relaying to Auth Command Service.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=OTPSendSerializer, summary="Send OTP SMS")
    def post(self, request: Request) -> Response:
        """
        Accepts and routes OTP trigger logic.
        """
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
    Thin layer relaying verification execution to Command boundary safely.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=OTPVerifySerializer, summary="Verify OTP and Login")
    def post(self, request: Request) -> Response:
        """
        Routes the validation check cleanly.
        """
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'OTP':
            return Response({"error": "احراز هویت پیامکی در سیستم غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dto = OTPVerifyDTO(
            identifier=serializer.validated_data['phone_number'],
            code=serializer.validated_data['code']
        )
        
        try:
            result: dict = AuthCommandService.verify_otp_and_login(dto)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmailRegisterView(generics.CreateAPIView):
    """
    Standard generic wrapper intercepting logic safely.
    """
    permission_classes = [AllowAny]
    serializer_class = EmailRegisterSerializer

    @extend_schema(summary="Register using Email")
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Replaces base logic via Command Service for full CQRS compatibility.
        """
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ثبت‌نام ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dto = EmailRegisterDTO(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        try:
            AuthCommandService.register_email(dto)
            return Response({"message": "ثبت نام با موفقیت انجام شد."}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmailLoginView(APIView):
    """
    Relays logic directly utilizing the specialized TokenObtainPair override safely.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(request=EmailLoginSerializer, summary="Login using Email")
    def post(self, request: Request) -> Response:
        """
        Validates login and echoes response token.
        """
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ورود ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Reuses existing OTP Command infrastructure seamlessly configured for Email Reset mode.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(request=PasswordResetRequestSerializer, summary="Request Email Password Reset")
    def post(self, request: Request) -> Response:
        """
        Routes the Reset request intelligently.
        """
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
    Invokes finalized reset logic properly separated within the Command Service.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(request=PasswordResetConfirmSerializer, summary="Confirm Email Password Reset")
    def post(self, request: Request) -> Response:
        """
        Completes process via cleanly segregated method.
        """
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