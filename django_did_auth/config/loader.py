from django.conf import settings
from .defaults import DID_AUTH as DEFAULTS

def get_config(path: str, default=None):
    user_config = getattr(settings, "DID_AUTH", {})
    keys = path.split(".")

    user_val = user_config
    default_val = DEFAULTS

    for key in keys:
        if isinstance(user_val, dict) and key in user_val:
            user_val = user_val[key]
        else:
            user_val = None

        if isinstance(default_val, dict) and key in default_val:
            default_val = default_val[key]
        else:
            default_val = default

    return user_val if user_val is not None else default_val

def get_admin_url():
    return get_config("ADMIN_URL", "admin/").strip("/") + "/"