"""
API Views for Unified Authentication (OTP or Email).
"""
from django.conf import settings
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from .models import UserAddress
from .serializers import (
    EmailRegisterSerializer, EmailLoginSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    OTPSendSerializer, OTPVerifySerializer, UserProfileSerializer, UserAddressSerializer
)
from .services import OTPAuthService

User = get_user_model()

def get_client_ip(request: Request) -> str:
    """Helper to extract real IP from request to prevent abuse."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


class AuthConfigView(APIView):
    """Provides the frontend with the active authentication mode."""
    permission_classes = [AllowAny]
    def get(self, request: Request) -> Response:
        mode = getattr(settings, 'AUTH_MODE', 'OTP')
        return Response({"mode": mode}, status=status.HTTP_200_OK)



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
            OTPAuthService.generate_and_send_otp(identifier=phone_number, ip_address=ip_address, is_email_reset=False)
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
    permission_classes = [AllowAny]
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "ورود ایمیلی غیرفعال است."}, status=status.HTTP_403_FORBIDDEN)
        serializer = EmailLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "این امکان فقط در حالت ایمیل فعال است."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        ip_address = get_client_ip(request)
        
        if not User.objects.filter(email=email).exists():
            return Response({"error": "کاربری با این ایمیل یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            OTPAuthService.generate_and_send_otp(identifier=email, ip_address=ip_address, is_email_reset=True)
            return Response({"message": "کد بازیابی رمز عبور به ایمیل شما ارسال شد."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    def post(self, request: Request) -> Response:
        if getattr(settings, 'AUTH_MODE', 'OTP') != 'EMAIL':
            return Response({"error": "این امکان فقط در حالت ایمیل فعال است."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            OTPAuthService.verify_reset_code_and_set_password(
                email=serializer.validated_data['email'],
                code=serializer.validated_data['code'],
                new_password=serializer.validated_data['new_password']
            )
            return Response({"message": "رمز عبور با موفقیت تغییر کرد. اکنون وارد شوید."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserAddressViewSet(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, uuid=None):
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response({"message": "آدرس پیش‌فرض با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)