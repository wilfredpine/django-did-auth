"""
django_sauth/security/ratelimit/decorators.py

Safe rate limiting decorator with Redis circuit breaker + fallback.
Fully reusable and consistent with the new logging system.
"""

import logging
import time
from functools import wraps

from django_redis import get_redis_connection
from django_ratelimit.decorators import ratelimit

from django_sauth.config.loader import get_config
from django_sauth.security.audit.logger import log_ratelimit_bypass, log_redis_down

logger = logging.getLogger('sauth.ratelimit')   # Consistent naming

REDIS_STATUS = {
    "is_available": True,
    "last_check": 0,
    "retry_after": 10,
}


def is_redis_available():
    """Circuit breaker for Redis availability"""
    now = time.time()

    # Fast path if recently marked unavailable
    if not REDIS_STATUS["is_available"] and now - REDIS_STATUS["last_check"] < REDIS_STATUS["retry_after"]:
        return False

    try:
        get_redis_connection("default").ping()
        REDIS_STATUS.update({"is_available": True, "last_check": now})
        return True
    except Exception as e:
        REDIS_STATUS.update({"is_available": False, "last_check": now})
        logger.warning("Redis unavailable — falling back to no rate limiting", 
                      extra={"event": "redis_down", "error": str(e)})
        log_redis_down(e)
        return False


def safe_ratelimit(key='ip', rate=None, **ratelimit_kwargs):
    """
    Safe rate limit decorator.
    
    Usage examples:
        @safe_ratelimit(key='ip', rate='10/m')
        @safe_ratelimit(key='post:email', rate='5/m')
        
    The 'rate' parameter can be a string like "10/m" or omitted (will use SAUTH config).
    """
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            # Determine rate from config if not explicitly passed
            actual_rate = rate
            if actual_rate is None:
                # Try to get from SAUTH config based on key
                if key == 'ip':
                    actual_rate = get_config("RATE_LIMIT.LOGIN", "10/m")
                elif key == 'post:email':
                    actual_rate = get_config("RATE_LIMIT.REGISTER", "5/m")  # fallback
                else:
                    actual_rate = "10/m"

            if is_redis_available():
                # Apply rate limiting only if Redis is up
                return ratelimit(
                    key=key,
                    rate=actual_rate,
                    **ratelimit_kwargs
                )(view)(request, *args, **kwargs)

            # Redis down → bypass + log
            log_ratelimit_bypass(request)
            logger.warning(
                "Rate limiting bypassed due to Redis outage",
                extra={
                    "event": "ratelimit_bypass",
                    "ip": request.META.get("REMOTE_ADDR"),
                    "path": request.path,
                    "method": request.method,
                }
            )
            # Continue without rate limiting (fail open)
            return view(request, *args, **kwargs)

        return wrapped
    return decorator