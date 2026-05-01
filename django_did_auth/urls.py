"""
django_did_auth/urls.py
Complete URL configuration for the django_did_auth framework.
"""

from django.urls import path
from django.shortcuts import render
from django_did_auth.core.views.register import register_view
from django_did_auth.core.views.login import login_view
from django_did_auth.core.views.logout import logout_view
from django_did_auth.core.views.activation import activate_account_view
from django_did_auth.core.views.password_reset import (
    password_reset_request_view,
    password_reset_confirm_view
)

app_name = "did_auth"

urlpatterns = [
    # Authentication
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Email Verification
    path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
    path("verification-sent/", 
         lambda r: render(r, "did_auth/verification_sent.html"), 
         name="verification_sent"),

    # Password Reset
    path("password-reset/", password_reset_request_view, name="password_reset_request"),
    path("password-reset-confirm/<uidb64>/<token>/", 
         password_reset_confirm_view, 
         name="password_reset_confirm"),
    
]