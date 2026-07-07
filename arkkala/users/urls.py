"""
URLs mapping for Users App.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AuthConfigView,
    OTPSendView, OTPVerifyView, 
    EmailRegisterView, EmailLoginView, 
    PasswordResetRequestView, PasswordResetConfirmView,
    UserProfileView
)

urlpatterns = [
    # General Profile & Config
    path('auth-config/', AuthConfigView.as_view(), name='auth_config'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Mode 1: OTP Routes
    path('otp/send/', OTPSendView.as_view(), name='otp_send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp_verify'),
    
    # Mode 2: Email Routes
    path('register/', EmailRegisterView.as_view(), name='register'),
    path('login/', EmailLoginView.as_view(), name='login'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]