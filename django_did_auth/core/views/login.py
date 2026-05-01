from django.shortcuts import render, redirect
from django.contrib import messages
from django_did_auth.security.ratelimit.decorators import safe_ratelimit
from django_did_auth.core.flows.login_flow import login_user
from django_did_auth.hooks.role_hooks import redirect_by_role
from django_did_auth.ui.adapters.form_adapter import get_form_class
from django_did_auth.config.loader import get_config

# Import logging at top level
from django_did_auth.security.audit.logger import (
    log_login_success,
    log_login_failure,
    log_login_blocked_inactive
)


@safe_ratelimit(key='ip', rate=get_config("RATE_LIMIT.LOGIN", "10/m"))
@safe_ratelimit(key='post:email', rate=get_config("RATE_LIMIT.LOGIN", "5/m"))
def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    FormClass = get_form_class("LoginForm")

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user, status = login_user(request, email, password)

            if status == "success":
                log_login_success(request, user)
                from django_did_auth.hooks.auth_hooks import on_login_success
                on_login_success(request, user)
                return redirect_by_role(user)

            elif status == "not_verified":
                log_login_blocked_inactive(request, email)
                messages.warning(request, "Account not verified. A new verification email has been sent.")
                return redirect("did_auth:verification_sent")

            # Invalid credentials
            log_login_failure(request, email)
            messages.error(request, "Invalid email or password.")
        else:
            # Form validation failed
            log_login_failure(request, form.cleaned_data.get("email"))
            messages.error(request, "Invalid email or password.")
    else:
        form = FormClass()

    return render(request, "did_auth/login.html", {"form": form})