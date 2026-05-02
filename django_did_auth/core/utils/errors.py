from django_did_auth.config.loader import get_config, get_callable
from django_did_auth.security.audit.logger import log_event

from django.shortcuts import render


def handle_error(request, code=403, message=None):
    """
    Unified error handler
    Supports:
    - pluggable overrides
    - logging
    - fallback templates
    """

    message = message or "An error occurred."

    # ======================
    # 1. LOGGING
    # ======================
    log_event(
        request,
        event=f"error_{code}",
        level="warning" if code >= 400 else "info",
        extra={"error_message": message}
    )

    # ======================
    # 2. PLUGGABLE HANDLER
    # ======================
    handler_path = get_config(f"ERROR_HANDLERS.{code}")

    if handler_path:
        func = get_callable(handler_path)
        if func:
            return func(request, message=message)

    # ======================
    # 3. DEFAULT TEMPLATE
    # ======================
    return render(
        request,
        f"did_auth/errors/{code}.html",
        {"message": message, "error_code": code},
        status=code
    )
    
def handle_404(request, exception=None):
    return handle_error(request, 404, "Page not found.")