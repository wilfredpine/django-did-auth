from django_did_auth.config.loader import get_config, get_admin_url
from django_did_auth.security.audit.logger import get_client_ip, audit_logger
from django_did_auth.core.utils.errors import handle_error

class AdminIPWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_path = "/" + get_admin_url()
    def __call__(self, request):
        # Skip in development
        # if settings.DEBUG:
        #     return self.get_response(request)
        path = request.path.rstrip("/") + "/"
        if path == self.admin_path or path.startswith(self.admin_path):
            allowed_ips = [ip.strip() for ip in get_config("ADMIN_IP_WHITELIST", ['127.0.0.1', '::1']) if ip.strip()]
            if allowed_ips:
                client_ip = get_client_ip(request)
                if client_ip not in allowed_ips:
                    audit_logger.warning(
                        "admin_access_blocked",
                        extra={"ip": client_ip, "path": request.path}
                    )
                    return handle_error(request, 403, "Your are not allowed to access the admin panel.")
        return self.get_response(request)
    