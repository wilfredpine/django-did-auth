from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django_sauth.config.loader import get_config
from django_sauth.security.audit.logger import log_logout   # Correct import


def logout_view(request):
    """Secure logout with audit logging"""
    if request.user.is_authenticated:
        log_logout(request, request.user)
        logout(request)
        messages.success(request, "You have been logged out successfully.")

    return redirect(get_config("LOGOUT_REDIRECT", "sauth:login"))