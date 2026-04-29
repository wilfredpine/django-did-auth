"""
django_sauth/core/flows/login_flow.py

Core login business logic with proper handling for inactive users.
"""

from django.contrib.auth import authenticate
from django_sauth.core.flows.email_flow import send_verification_email
from django_sauth.core.tokens.activation import generate_activation_token
from django_sauth.security.audit.logger import (
    log_login_success,
    log_login_failure,
    log_login_blocked_inactive
)


def login_user(request, email, password):
    """
    Authenticate user and handle inactive accounts by resending verification email.
    Returns (user, status) tuple.
    """
    user = authenticate(request, username=email, password=password)

    if not user:
        log_login_failure(request, email)
        return None, "invalid_credentials"

    if not user.is_active:
        # Resend verification email automatically
        uid, token = generate_activation_token(user)
        send_verification_email(request, user, uid, token)
        
        log_login_blocked_inactive(request, email)
        return None, "not_verified"

    # Successful login
    log_login_success(request, user)
    return user, "success"