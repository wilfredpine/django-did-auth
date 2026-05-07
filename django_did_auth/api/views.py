      
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_did_auth.core.flows.login_flow import login_user # use your existing flow
from django_did_auth.security.audit.logger import log_event, log_password_reset_requested, log_password_reset_completed, log_password_change
from axes.handlers.proxy import AxesProxyHandler
from rest_framework.permissions import IsAuthenticated
from django_did_auth.api.permissions import role_access
from django_did_auth.core.flows.register_flow import register_user
from django_did_auth.config.loader import get_config
from django_did_auth.security.ratelimit.decorators import safe_ratelimit
from django_did_auth.core.flows.password_flow import request_password_reset, confirm_password_reset, change_password_flow
from django.contrib.auth import update_session_auth_hash

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django_did_auth.security.ratelimit.api_throttles import (
    PublicThrottle,
    AuthenticatedThrottle,
    LoginIPThrottle,
    LoginEmailThrottle,
    RegisterIPThrottle,
    RegisterEmailThrottle,
    PasswordResetRequestThrottle,
    PasswordResetConfirmThrottle,
    ChangePasswordThrottle,
)

from rest_framework.exceptions import Throttled

def blacklist_user_tokens(user):
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)
        
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    if isinstance(exc, Throttled):
        return Response(
            {"error": "rate_limited", "detail": str(exc.detail)},
            status=429,
        )
    return exception_handler(exc, context)
        
class HealthCheckAPIView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({
            "status": "ok",
            "service": "django-did-auth API"
        })
        

class APILoginView(APIView):
    authentication_classes = []  # no auth needed for login
    permission_classes = [AllowAny]

    throttle_classes = [
        LoginIPThrottle,     # per IP
        LoginEmailThrottle,  # per email
    ]
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            result = login_user(
                request,
                email,
                password,
                use_session=False
            )

            # normalize return
            if isinstance(result, tuple):
                user, error = result
            else:
                user = result
                error = None
                
            if AxesProxyHandler.is_locked(request):
                log_event(request, "api_login_account_locked", extra={"email": email})
                return Response(
                    {"error": "account_locked"},
                    status=status.HTTP_423_LOCKED
                )

            if not user:
                log_event(request, "api_login_failure", extra={"email": email})
                return Response(
                    {"error": error or "invalid_credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not user.is_active:
                log_event(request, "api_login_inactive", extra={"email": email})
                return Response(
                    {"error": "inactive_account"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Generate JWT tokens
            refresh = RefreshToken()
            # refresh = RefreshToken.for_user(user)
            refresh["user_id"] = str(user.pk)  # force string
            refresh["role"] = getattr(user, "role", "user")
            
            access = refresh.access_token

            log_event(request, "api_login_success", user=user)

            return Response({
                "access": str(access),
                "refresh": str(refresh),
            })

        except Exception as e:
            log_event(request, "api_login_exception", extra={"error": str(e)})
            return Response(
                {"error": "login_failed", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        logout_all = request.data.get("all", False)

        try:
            if logout_all:
                # GLOBAL LOGOUT
                for token in OutstandingToken.objects.filter(user=request.user):
                    BlacklistedToken.objects.get_or_create(token=token)

                return Response({"status": "logged_out_all"})

            # SINGLE SESSION LOGOUT
            if not refresh_token:
                return Response({"error": "missing_refresh"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"status": "logged_out"})

        except Exception as e:
            return Response({"error": "invalid_token"}, status=400)
        

class TokenRefreshAPIView(APIView):
    authentication_classes = []  # public
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "missing_refresh_token"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)

            # Rotation happens here: issue NEW access (and optionally new refresh)
            new_access = refresh.access_token

            # If BLACKLIST_AFTER_ROTATION=True, blacklist old refresh:
            try:
                refresh.blacklist()
            except Exception:
                pass  # blacklist app might not be enabled yet

            # Issue a NEW refresh token (rotation)
            new_refresh = RefreshToken.for_user(request.user) if request.user.is_authenticated else RefreshToken()
            # If user is not attached, copy claims manually:
            if not request.user.is_authenticated:
                # carry forward user_id/role from old token
                new_refresh["user_id"] = str(refresh.get("user_id"))
                if "role" in refresh:
                    new_refresh["role"] = refresh["role"]

            return Response({
                "access": str(new_access),
                "refresh": str(new_refresh),
            })

        except Exception as e:
            return Response({"error": "invalid_refresh"}, status=401)
        
        
class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    throttle_classes = [
        RegisterIPThrottle,     # per IP
        RegisterEmailThrottle,  # per email
    ]
    def post(self, request):
        try:
            # reuse your existing flow
            user = register_user(request, request.data)

            log_event(request, "api_register_success", user=user)

            return Response({
                "message": "Registration successful. Please verify your email."
            }, status=201)

        except Exception as e:
            log_event(request, "api_register_failure", extra={"error": str(e)})
            return Response({
                "error": "registration_failed",
                "detail": str(e)
            }, status=400)
            
            

class PasswordResetRequestAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    throttle_classes = [
        PasswordResetRequestThrottle,
    ]
    def post(self, request):
        try:
            email = request.data.get("email")
            user, uid, token = request_password_reset(request, email)

            if user:
                from django_did_auth.core.flows.email_flow import send_password_reset_email
                send_password_reset_email(request, user, uid, token)
                
                log_password_reset_requested(request, email)  

            return Response({
                "message": "If the email exists, a reset link has been sent."
            })

        except Exception:
            # never leak user existence
            return Response({
                "message": "If the email exists, a reset link has been sent."
            })
            

class PasswordResetConfirmAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    throttle_classes = [
        PasswordResetConfirmThrottle,
    ]
    def post(self, request):
        try:
            uid = request.data.get("uid")
            token = request.data.get("token")
            new_password = request.data.get("new_password")
            user, status = confirm_password_reset(request, uid, token, new_password)
                
            if status == "success":
                blacklist_user_tokens(user)
                log_password_reset_completed(request, user)       
                return Response({
                    "message": "Password has been reset successfully."
                })
            else:
                log_event(request, "password_reset_confirm_failed", extra={"uid": uid, "token": token})
                return Response({
                    "error": "invalid_or_expired_token"
                }, status=400)

        except Exception:
            return Response({
                "error": "invalid_or_expired_token"
            }, status=400)

            
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    throttle_classes = [
        ChangePasswordThrottle
    ]
    def post(self, request):
        
        new_password = request.data.get("new_password")

        try:
            change_password_flow(
                user=request.user,
                new_password=new_password,
            )

            log_password_change(request, request.user)
            
            update_session_auth_hash(request, request.user)
            
            blacklist_user_tokens(request.user)

            return Response({
                "message": "Password updated successfully."
            })
        except Exception as e:
            log_event(
                request,
                "password_change_failed",
                user=request.user,
                level="warning",
                extra={"error": str(e)}
            )
            return Response({
                "error": "password_change_failed",
                "detail": str(e)
            }, status=400)
            

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user_id": request.user.id,
            "email": request.user.email,
            "role": getattr(request.user, "role", None),
        })
        
        
class AdminOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, role_access('admin')]

    def get(self, request):
        return Response({"message": "Admin access granted"})
    
class UserOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, role_access('user')]

    def get(self, request):
        return Response({"message": "User access granted"})
    
