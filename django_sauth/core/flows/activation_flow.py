from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone
from django_sauth.core.tokens.activation import account_activation_token, is_token_expired
from django_sauth.config.loader import get_config
from django_sauth.security.audit.logger import log_account_activation

def activate_user(uidb64, token, request=None):
    """Activate user account with expiry check"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return None, "invalid"

    if not account_activation_token.check_token(user, token):
        return None, "invalid"

    if is_token_expired(user):
        return None, "expired"

    user.is_active = True
    user.save()

    if request:
        log_account_activation(request, user)

    return user, "success"