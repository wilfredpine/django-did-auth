"""
django_did_auth/core/flows/password_flow.py
Password reset business logic.
"""

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django_did_auth.security.audit.logger import (
    log_password_reset_requested,
    log_password_reset_completed
)


def request_password_reset(request, email):
    """Request password reset — prevents user enumeration"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    log_password_reset_requested(request, email)

    try:
        user = User.objects.get(email=email, is_active=True)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return user, uid, token
    except User.DoesNotExist:
        return None, None, None   # Silent fail for security


def confirm_password_reset(request, uidb64, token, new_password):
    """Confirm password reset and update password"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return None, "invalid"

    if not default_token_generator.check_token(user, token):
        return None, "invalid"

    user.set_password(new_password)
    user.save()

    log_password_reset_completed(request, user)
    return user, "success"