from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django_did_auth.ui.adapters.form_adapter import get_form_class
from django_did_auth.core.flows.password_flow import change_password_flow
from django_did_auth.security.audit.logger import log_password_change, log_event
from django_did_auth.security.ratelimit.decorators import safe_ratelimit
from django.contrib.auth import update_session_auth_hash

@login_required
@safe_ratelimit(key="user", rate="5/m", block=True)
def change_password_view(request):
    
    FormClass = get_form_class("ChangePasswordForm")
    if request.method == "POST":
        
        form = FormClass(request.user, request.POST)

        if form.is_valid():
            change_password_flow(
                user=request.user,
                new_password=form.cleaned_data["new_password"]
            )

            log_password_change(request, request.user)
            
            update_session_auth_hash(request, request.user)

            messages.success(request, "Password updated successfully.")
            return redirect('did_auth:logout')  # or dashboard

        else:
            log_event(
                request,
                "password_change_failed",
                user=request.user,
                level="warning",
                extra={"errors": form.errors}
            )
            messages.error(request, "Password incorrect.")
    else:
        form = FormClass(request.user)

    return render(request, "profile/change_password.html", {"form": form})