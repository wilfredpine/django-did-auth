"""
django_sauth/core/flows/email_flow.py

Centralized, reusable email sending for authentication flows.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django_sauth.config.loader import get_config


def send_auth_email(request, user, template_name: str, subject: str, context: dict = None):
    """
    Reusable email sender for the entire framework and external use.
    
    Args:
        request: HttpRequest (needed for build_absolute_uri)
        user: CustomUser instance
        template_name: e.g. "activation.html" or "password_reset.html"
        subject: Email subject
        context: Additional context for the template (optional)
    """
    if context is None:
        context = {}

    context.update({
        'user': user,
        'expiry': get_config("EMAIL.VERIFY_EXPIRY_HOURS", 24) if "activation" in template_name else 
                  get_config("EMAIL.RESET_EXPIRY_HOURS", 1)
    })

    html_message = render_to_string(f"sauth/email/{template_name}", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=html_message,
        from_email=get_config("EMAIL.FROM_EMAIL"),
        to=[user.email]
    )
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=False)


# Specific convenience functions (easy to use)

def send_verification_email(request, user, uid, token):
    """Send account activation email"""
    activation_link = request.build_absolute_uri(
        reverse('sauth:activate', kwargs={'uidb64': uid, 'token': token})
    )

    send_auth_email(
        request=request,
        user=user,
        template_name="activation.html",
        subject="Activate your account",
        context={'activation_link': activation_link}
    )


def send_password_reset_email(request, user, uid, token):
    """Send password reset email"""
    reset_link = request.build_absolute_uri(
        reverse('sauth:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    )

    send_auth_email(
        request=request,
        user=user,
        template_name="password_reset.html",
        subject="Reset Your Password",
        context={'reset_link': reset_link}
    )
    
    
def send_general_email(request, user, subject: str, template_name: str, context: dict = None):
    """
    General purpose email sender that can be imported and used from anywhere in your project.
    
    Example usage outside django_sauth:
        from django_sauth.core.flows.email_flow import send_general_email
        send_general_email(request, user, "Welcome!", "welcome.html", {"extra": "data"})
    """
    send_auth_email(request, user, template_name, subject, context)