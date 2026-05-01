from django.shortcuts import render, redirect
from django.contrib import messages
from django_did_auth.security.ratelimit.decorators import safe_ratelimit
from django_did_auth.core.flows.register_flow import register_user
from django_did_auth.ui.adapters.form_adapter import get_form_class
from django_did_auth.config.loader import get_config

# Import logging functions at the top
from django_did_auth.security.audit.logger import log_register_success, log_register_failure


@safe_ratelimit(key='ip', rate=get_config("RATE_LIMIT.REGISTER", "5/m"))
@safe_ratelimit(key='post:email', rate=get_config("RATE_LIMIT.REGISTER", "5/m"))
def register_view(request):
    if request.user.is_authenticated:
        return redirect(get_config("LOGIN_REDIRECT", "/dashboard/"))

    FormClass = get_form_class("RegistrationForm")

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            user = register_user(request, form)
            
            log_register_success(request, user)                    
            messages.success(request, "Registration successful! Please check your email to activate your account.")
            return redirect("did_auth:verification_sent")
        else:
            log_register_failure(request, form.errors)            
            # Optionally add user-facing error
            messages.error(request, "Please correct the errors below.")
    else:
        form = FormClass()

    return render(request, "did_auth/register.html", {"form": form})