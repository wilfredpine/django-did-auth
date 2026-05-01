DID_AUTH = {
    "LOGIN_REDIRECT": "/dashboard/",
    "LOGOUT_REDIRECT": "/login/",
    "ADMIN_URL": "admin/",
    "ADMIN_IP_WHITELIST": ['127.0.0.1', '::1'],  # Localhost by default

    "ROLES": {
        "admin": "/admin-dashboard/",
        "staff": "/staff-dashboard/",
        "moderator": "/moderator-dashboard/",
        "user": "/dashboard/",
    },

    "EMAIL": {
        "VERIFY_EXPIRY_HOURS": 24,
        "RESET_EXPIRY_HOURS": 1,
        "FROM_EMAIL": None,  # Will use DEFAULT_FROM_EMAIL
    },

    "RATE_LIMIT": {
        "LOGIN": "10/m",
        "REGISTER": "5/m",
        "PASSWORD_RESET": "5/m",
    },

    "UI_FRAMEWORK": "tailwind",  # "tailwind" or "bootstrap"

    "ENABLE_AUDIT": True,
    "TRUST_PROXY": False,
    
    "SECURITY": {
        "PASSWORD_MIN_LENGTH": 12,
        "ENABLE_AXES": True,
        "LOCKOUT_AFTER_ATTEMPTS": 5,
        "LOCKOUT_DURATION_MINUTES": 30,
        "REQUIRE_HTTPS": True,          # Enforce in production
    },
    "AUDIT": {
        "ENABLED": True,
        "LOG_SENSITIVE": False,         # Don't log passwords
    }
    
}