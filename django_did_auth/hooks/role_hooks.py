from django.shortcuts import redirect
from django_did_auth.config.loader import get_config

def redirect_by_role(user):
    """Role-based redirect after login"""
    roles = get_config("ROLES", {})
    default = get_config("LOGIN_REDIRECT", "/dashboard/")
    return redirect(roles.get(getattr(user, 'role', 'user'), default))