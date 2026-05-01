from datetime import timedelta
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from django_did_auth.config.loader import get_config


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _get_user_secret(self, user):
        """Make token unique per user + status + email"""
        return str(user.pk) + str(user.date_joined) + str(user.is_active) + str(user.email)


account_activation_token = AccountActivationTokenGenerator()


def generate_activation_token(user):
    """Generate uid + token and store creation timestamp"""
    user.activation_token_created = timezone.now()
    user.save(update_fields=['activation_token_created'])

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    return uid, token


def is_token_expired(user, hours=None):
    """Check if activation token has expired"""
    if hours is None:
        hours = get_config("EMAIL.VERIFY_EXPIRY_HOURS", 24)
    
    if not getattr(user, 'activation_token_created', None):
        return True
    
    return timezone.now() > user.activation_token_created + timedelta(hours=hours)