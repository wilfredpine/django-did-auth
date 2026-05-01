from django.shortcuts import redirect
from django.contrib import messages
from django_did_auth.core.flows.activation_flow import activate_user


def activate_account_view(request, uidb64, token):
    user, status = activate_user(uidb64, token, request)

    if status == "success":
        messages.success(request, "Your account has been activated successfully. You can now log in.")
        return redirect("did_auth:login")

    elif status == "expired":
        messages.warning(request, "Activation link has expired. Please try logging in again to receive a new one.")
        return redirect("did_auth:login")

    else:
        messages.error(request, "Invalid activation link.")
        return redirect("did_auth:login")