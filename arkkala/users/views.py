"""
API Views for Unified Authentication (OTP or Email).
"""
from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from django.contrib.auth import get_user_model

from .serializers import (
    EmailRegisterSerializer, EmailLoginSerializer, 
    OTPSendSerializer, OTPVerifySerializer, UserProfileSerializer
)
from .services import OTPAuthService

User = get_user_model()


def get_client_ip(request: Request) -> str:
    """Helper to extract real IP from request to prevent abuse."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')



class OTPSendView(APIView):
    """Send SMS OTP for login/register."""
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'OTP':
            return Response({"error": "احراز هویت پیامکی در سیستم غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        ip_address = get_client_ip(request)
        
        try:
            OTPAuthService.generate_and_send_otp(phone_number, ip_address)
            return Response({"message": "کد تایید با موفقیت ارسال شد."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    """Verify OTP and return JWT Tokens."""
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'OTP':
            return Response({"error": "احراز هویت پیامکی در سیستم غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = OTPAuthService.verify_otp_and_login(
                serializer.validated_data['phone_number'],
                serializer.validated_data['code']
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class EmailRegisterView(generics.CreateAPIView):
    """Register User with Email and Password."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EmailRegisterSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ثبت‌نام ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "ثبت نام با موفقیت انجام شد."}, status=status.HTTP_201_CREATED)


class EmailLoginView(APIView):
    """Login User with Email and Password returning JWT."""
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ورود ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)



class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or Update User Profile details."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user