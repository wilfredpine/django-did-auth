"""
django_sauth/security/audit/logger.py

Centralized, reusable, and production-ready logging for the auth framework.
Compatible with your main project's LOGGING configuration.
"""

import logging
from django_sauth.config.loader import get_config

# Two dedicated loggers
audit_logger = logging.getLogger('sauth.audit')   # Security events → security_file
app_logger = logging.getLogger('sauth.app')       # General events → app_file


def get_client_ip(request):
    """Robust client IP detection"""
    if cf_ip := request.META.get("HTTP_CF_CONNECTING_IP"):
        return cf_ip
    if get_config("TRUST_PROXY", False) and (xff := request.META.get("HTTP_X_FORWARDED_FOR")):
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_event(
    request=None,
    event: str = "",
    user=None,
    email: str = None,
    level: str = "info",
    extra: dict = None
):
    """
    Main reusable logging function.
    Can be called from anywhere in your project.
    """
    ctx = {
        "event": event,
        "ip": get_client_ip(request) if request else None,
        "user_id": getattr(user, "id", None) if user else None,
        "email": email or (getattr(user, "email", None) if user else None),
        "path": getattr(request, "path", None),
    }
    if extra:
        ctx.update(extra)

    SECURITY_EVENTS = {"login", "password", "activation", "register"}

    is_security = any(k in event for k in SECURITY_EVENTS)
    logger = audit_logger if is_security else app_logger

    lvl = level.lower()

    if lvl == "error":
        logger.error(event, extra=ctx)
    elif lvl == "warning":
        logger.warning(event, extra=ctx)
    else:
        logger.info(event, extra=ctx)


# ====================== Convenience Functions ======================

def log_register_success(request, user):
    log_event(request, "register_success", user=user)

def log_register_failure(request, errors=None):
    log_event(request, "register_failure", extra={"errors": str(errors)} if errors else None)

def log_login_success(request, user):
    log_event(request, "login_success", user=user)

def log_login_failure(request, email):
    log_event(request, "login_failure", email=email, level="warning")

def log_login_blocked_inactive(request, email):
    log_event(request, "login_blocked_inactive", email=email, level="warning")

def log_account_activation(request, user):
    log_event(request, "account_activation", user=user)

def log_password_reset_requested(request, email):
    log_event(request, "password_reset_requested", email=email)

def log_password_reset_completed(request, user):
    log_event(request, "password_reset_completed", user=user)

def log_logout(request, user):
    log_event(request, "logout", user=user)

def log_ratelimit_bypass(request):
    log_event(request, "ratelimit_bypass", level="warning")

def log_redis_down(error):
    audit_logger.warning("Redis unavailable", extra={"event": "redis_down", "error": str(error)})