from django.urls import path
from .views import (
    ChangePasswordAPIView,
    APILoginView, 
    LogoutAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView, 
    RegisterAPIView,
    ProfileAPIView, 
    TokenRefreshAPIView,
)

# from .views import HealthCheckAPIView, AdminOnlyAPIView, UserOnlyAPIView

urlpatterns = [
    # JWT Token Refresh Endpoint
    path("refresh/", TokenRefreshAPIView.as_view(), name="api-refresh"),
    
    # Authentication Endpoints
    path("register/", RegisterAPIView.as_view(), name="api-register"),
    path("login/", APILoginView.as_view(), name="api-login"),
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    
    # Password Reset Endpoints
    path("password-reset/", PasswordResetRequestAPIView.as_view(), name="api-password-reset-request"),
    path("password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmAPIView.as_view(), name="api-password-reset-confirm"),
    
    # User Profile & Password Change (Authenticated Endpoints)
    path("profile/", ProfileAPIView.as_view(), name="api-profile"),
    path("password-change/", ChangePasswordAPIView.as_view(), name="api-password-change"), 
    
]

 # Role-Based Access Control Endpoints Examples
"""
path("health/", HealthCheckAPIView.as_view(), name="api-health"),
path("admin-only/", AdminOnlyAPIView.as_view(), name="api-admin-only"),
path("user-only/", UserOnlyAPIView.as_view(), name="api-user-only"),
"""