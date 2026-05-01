"""
django_did_auth/ui/adapters/form_adapter.py

Dynamically selects form classes based on DID_AUTH["UI_FRAMEWORK"] setting.
"""

from django_did_auth.config.loader import get_config


def get_form_class(form_type: str):
    """Return the appropriate form class based on configured UI framework."""
    ui = get_config("UI_FRAMEWORK", "tailwind")

    if ui == "bootstrap":
        from django_did_auth.ui.forms.bootstrap import (
            RegistrationForm,
            LoginForm,
            PasswordResetRequestForm,
            SetNewPasswordForm,
            ResendVerificationForm,   # kept for future use
        )
    else:
        from django_did_auth.ui.forms.tailwind import (
            RegistrationForm,
            LoginForm,
            PasswordResetRequestForm,
            SetNewPasswordForm,
            ResendVerificationForm,
        )

    forms_dict = {
        "RegistrationForm": RegistrationForm,
        "LoginForm": LoginForm,
        "PasswordResetRequestForm": PasswordResetRequestForm,
        "SetNewPasswordForm": SetNewPasswordForm,
        "ResendVerificationForm": ResendVerificationForm,
    }

    form_class = forms_dict.get(form_type)
    if not form_class:
        raise ValueError(f"Unknown form type: {form_type}")
    
    return form_class