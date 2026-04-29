from django.conf import settings
from .defaults import SAUTH as DEFAULTS

def get_config(path: str, default=None):
    """Safe nested getter with better fallback"""
    config = getattr(settings, "SAUTH", {})
    keys = path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, DEFAULTS.get(key, default) if isinstance(DEFAULTS, dict) else default)
        else:
            return default
    return value if value is not None else default