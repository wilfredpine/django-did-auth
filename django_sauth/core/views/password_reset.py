from django.shortcuts import render, redirect
from django.contrib import messages
from django_sauth.security.ratelimit.decorators import safe_ratelimit
from django_sauth.core.flows.password_flow import request_password_reset, confirm_password_reset
from django_sauth.ui.adapters.form_adapter import get_form_class
from django_sauth.config.loader import get_config

# Import logging functions
from django_sauth.security.audit.logger import (
    log_password_reset_requested,
    log_password_reset_completed
)


@safe_ratelimit(key='ip', rate=get_config("RATE_LIMIT.PASSWORD_RESET", "5/m"))
@safe_ratelimit(key='post:email', rate=get_config("RATE_LIMIT.PASSWORD_RESET", "5/m"))
def password_reset_request_view(request):
    FormClass = get_form_class("PasswordResetRequestForm")

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user, uid, token = request_password_reset(request, email)

            if user:
                from django_sauth.core.flows.email_flow import send_password_reset_email
                send_password_reset_email(request, user, uid, token)
                
                log_password_reset_requested(request, email)      # ← Added

            # Always show success (security best practice)
            messages.success(request, "If an account exists with that email, a password reset link has been sent.")
            return redirect("sauth:login")
        else:
            # Optional: log failed form submission
            pass
    else:
        form = FormClass()

    return render(request, "sauth/password_reset_request.html", {"form": form})


def password_reset_confirm_view(request, uidb64, token):
    FormClass = get_form_class("SetNewPasswordForm")

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            user, status = confirm_password_reset(request, uidb64, token, form.cleaned_data["new_password"])
            
            if status == "success":
                log_password_reset_completed(request, user)       # ← Added
                messages.success(request, "Your password has been reset successfully.")
                return redirect("sauth:login")
            else:
                messages.error(request, "Invalid or expired reset link.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FormClass()

    return render(request, "sauth/password_reset_confirm.html", {"form": form, "valid_link": True})