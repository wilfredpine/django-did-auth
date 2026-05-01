from django.contrib.auth import get_user_model
from django_did_auth.core.tokens.activation import generate_activation_token
from django_did_auth.core.flows.email_flow import send_verification_email

User = get_user_model()

def register_user(request, form):
    """Register user as inactive and send verification email"""
    user = form.save(commit=False)
    user.is_active = False
    user.save()

    uid, token = generate_activation_token(user)
    send_verification_email(request, user, uid, token)

    return user