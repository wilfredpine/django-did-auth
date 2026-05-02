from functools import wraps
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from django_did_auth.config.loader import get_config
from django_did_auth.security.audit.logger import log_event

from django_did_auth.core.utils.errors import handle_error

def role_required(*allowed_roles):
    """
    Role-based access decorator with smart redirect
    """

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user

            user_role = getattr(user, "role", None)

            # Allow access
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            if get_config("DENY_BEHAVIOR") == "forbidden":
                log_event(
                    request,
                    "role_access_denied",
                    user=user,
                    level="warning",
                    extra={"required": allowed_roles, "actual": user_role}
                )
                return handle_error(request, 403, "You are not allowed to access this page.")

            # Redirect to correct dashboard
            dashboard_map = get_config("ROLES", {})

            redirect_url = dashboard_map.get(user_role)

            if redirect_url:
                log_event(
                    request,
                    "role_access_redirected",
                    user=user,
                    level="warning",
                    extra={"required": allowed_roles, "actual": user_role}
                )
                return redirect(redirect_url)

            # fallback
            return redirect(get_config("LOGIN_REDIRECT", "/"))

        return _wrapped
    return decorator