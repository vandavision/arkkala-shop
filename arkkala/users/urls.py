"""
URLs mapping for Users App.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    OTPSendView, OTPVerifyView, 
    EmailRegisterView, EmailLoginView, 
    UserProfileView
)

urlpatterns = [
    # General Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Mode 1: OTP Routes
    path('otp/send/', OTPSendView.as_view(), name='otp_send'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp_verify'),
    
    # Mode 2: Email Routes
    path('register/', EmailRegisterView.as_view(), name='register'),
    path('login/', EmailLoginView.as_view(), name='login'),
]