import logging
import time

from rest_framework.throttling import SimpleRateThrottle

from django_redis import get_redis_connection

from django_did_auth.security.audit.logger import (
    log_ratelimit_bypass,
    log_redis_down,
    log_event,
)

logger = logging.getLogger("did_auth.ratelimit")


# =========================================================
# REDIS CIRCUIT BREAKER
# =========================================================
REDIS_STATUS = {
    "is_available": True,
    "last_check": 0,
    "retry_after": 10,
}


def is_redis_available():
    now = time.time()

    if (
        not REDIS_STATUS["is_available"]
        and now - REDIS_STATUS["last_check"] < REDIS_STATUS["retry_after"]
    ):
        return False

    try:
        get_redis_connection("default").ping()
        REDIS_STATUS.update({"is_available": True, "last_check": now})
        return True
    except Exception as e:
        REDIS_STATUS.update({"is_available": False, "last_check": now})

        logger.warning(
            "Redis unavailable — throttling bypass",
            extra={"event": "redis_down", "error": str(e)},
        )

        log_redis_down(e)
        return False


# =========================================================
# BASE SAFE THROTTLE
# =========================================================
class SafeSimpleRateThrottle(SimpleRateThrottle):
    """
    Base throttle:
    - Redis-aware (fail-open)
    - Central logging
    """

    scope = None  # MUST be defined in subclass

    def allow_request(self, request, view):
        if not is_redis_available():
            log_ratelimit_bypass(request)
            return True

        allowed = super().allow_request(request, view)

        if not allowed:
            log_event(
                request,
                "api_rate_limit_hit",
                level="warning",
                extra={
                    "scope": self.scope,
                    "ident": self.get_ident(request),
                },
            )

        return allowed


# =========================================================
# GENERAL THROTTLES (GLOBAL SAFETY NET)
# =========================================================

class PublicThrottle(SafeSimpleRateThrottle):
    """
    Applies to anonymous users
    """
    scope = "api_public"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None
        return f"{self.scope}:{self.get_ident(request)}"


class AuthenticatedThrottle(SafeSimpleRateThrottle):
    """
    Applies to authenticated users
    """
    scope = "api_authenticated"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return f"{self.scope}:{request.user.id}"


# =========================================================
# LOGIN THROTTLES
# =========================================================

class LoginIPThrottle(SafeSimpleRateThrottle):
    scope = "login_ip"

    def get_cache_key(self, request, view):
        return f"{self.scope}:{self.get_ident(request)}"


class LoginEmailThrottle(SafeSimpleRateThrottle):
    scope = "login_email"

    def get_cache_key(self, request, view):
        email = request.data.get("email")
        if not email:
            return None
        return f"{self.scope}:{email.lower()}"


# =========================================================
# REGISTER THROTTLES
# =========================================================

class RegisterIPThrottle(SafeSimpleRateThrottle):
    scope = "register_ip"

    def get_cache_key(self, request, view):
        return f"{self.scope}:{self.get_ident(request)}"


class RegisterEmailThrottle(SafeSimpleRateThrottle):
    scope = "register_email"

    def get_cache_key(self, request, view):
        email = request.data.get("email")
        if not email:
            return None
        return f"{self.scope}:{email.lower()}"


# =========================================================
# PASSWORD RESET THROTTLES
# =========================================================

class PasswordResetRequestThrottle(SafeSimpleRateThrottle):
    scope = "password_reset_request"

    def get_cache_key(self, request, view):
        email = request.data.get("email")
        if not email:
            return None
        return f"{self.scope}:{email.lower()}"


class PasswordResetConfirmThrottle(SafeSimpleRateThrottle):
    scope = "password_reset_confirm"

    def get_cache_key(self, request, view):
        return f"{self.scope}:{self.get_ident(request)}"


# =========================================================
# CHANGE PASSWORD (AUTH)
# =========================================================

class ChangePasswordThrottle(SafeSimpleRateThrottle):
    scope = "change_password"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return f"{self.scope}:{request.user.id}"
    
from rest_framework.throttling import SimpleRateThrottle

# =========================================================
# Public Read-Only Throttle 
# =========================================================
class PublicReadOnlyThrottle(SafeSimpleRateThrottle):
    """
    Throttle for public READ-only endpoints.
    Applies only to GET/HEAD/OPTIONS and only for anonymous users.
    """
    scope = "api_public_readonly"

    def get_cache_key(self, request, view):
        # Only throttle safe methods
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            return None

        # Only for anonymous users (public)
        if request.user and request.user.is_authenticated:
            return None

        return f"{self.scope}:{self.get_ident(request)}"
    

class MethodAwarePublicThrottle(SafeSimpleRateThrottle):
    def get_cache_key(self, request, view):
        method = request.method.lower()
        return f"public_{method}:{self.get_ident(request)}"
    

class APIKeyThrottle(SafeSimpleRateThrottle):
    """
    Optional throttle for API-key based access.

    Requires:
        request.api_key with attribute `prefix`
    """

    scope = "api_key"

    def get_cache_key(self, request, view):
        api_key = getattr(request, "api_key", None)

        if not api_key:
            return None  # not applicable

        prefix = getattr(api_key, "prefix", None)
        if not prefix:
            return None

        return f"{self.scope}:{prefix}"