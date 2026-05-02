# 🔐 django-did-auth

A production-grade authentication framework for Django with:

- Email-based authentication
- Role-based redirection
- Built-in security hardening
- Rate limiting & brute-force protection
- Extensible architecture

---

## 🚀 Features

✅ Register with email verification  
✅ Login / Logout  
✅ Forgot Password (secure token flow)  
✅ Change Password
✅ Role-based redirects  
✅ Tailwind / Bootstrap UI support  
✅ Redis-backed rate limiting  
✅ Axes brute-force protection  
✅ Audit logging (SIEM-ready)

---

## ⚙️ Installation

```bash
pip install django-did-auth
```

---

## 🔧 Setup

### 1. Add to INSTALLED_APPS

```python
# --------------------------------------------------
#  🔐 AUTHENTICATION & DID_AUTH CONFIG
# --------------------------------------------------
INSTALLED_APPS += [
    'django_did_auth', # install here
    'axes', 
    'django_ratelimit',
    'users', # apps for custom user model
]
```

---

### 2. URLs

#### Using full authentication:
- `your_project/urls.py`

```python

from django.views.generic.base import RedirectView
from django_did_auth.core.views.password import change_password_view

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # DID_AUTH URLs
    path('auth/', include('django_did_auth.urls')), # Include DID_AUTH URLs
    path('', RedirectView.as_view(pattern_name='did_auth:login', permanent=False)),
    path('profile/change-password/', change_password_view, name="change_password"), 

    # 👤 Role Dashboards
    path('dashboard/admin/', main_views.admin_dashboard),
    path('dashboard/', main_views.user_dashboard),
]
```

#### Or using only specific authentication:
- create `urls.py` at your app where custom_user model made
- Example: `your_project/user_app/urls.py`

```python

from django.urls import path
from django.shortcuts import render
from django_did_auth.core.views.register import register_view
from django_did_auth.core.views.login import login_view
from django_did_auth.core.views.logout import logout_view
from django_did_auth.core.views.activation import activate_account_view
from django_did_auth.core.views.password_reset import (
    password_reset_request_view,
    password_reset_confirm_view
)

app_name = "did_auth"

urlpatterns = [
    # Authentication
    # path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Email Verification
    # path("activate/<uidb64>/<token>/", activate_account_view, name="activate"),
    # path("verification-sent/", lambda r: render(r, "did_auth/verification_sent.html"), name="verification_sent"),

    # Password Reset
    # path("password-reset/", password_reset_request_view, name="password_reset_request"),
    # path("password-reset-confirm/<uidb64>/<token>/", password_reset_confirm_view, name="password_reset_confirm"),
]

```

then include it on url project urls
- - `your_project/urls.py`

```python
from django.contrib import admin
from django.urls import include, path

from core_system import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('user_app.urls')), # from `your_project/user_app/urls.py`
    ...
]

```

IMPORTANT: for disabling / or using specific authentication, use custom Templates (see below)

---

### 3. Required Settings

```python
AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = 'did_auth:login'

DID_AUTH = {
    # "LOGIN_REDIRECT": "/dashboard/", # already redirect based on roles below
    "LOGOUT_REDIRECT": "/auth/login/",

    "ADMIN_URL": "admin/",
    "ADMIN_IP_WHITELIST": ['127.0.0.1', '::1'],  # Localhost by default
    # on your URL
    # from django_did_auth.config.loader import get_admin_url
    # urlpatterns = [
    #     path(get_admin_url(), admin.site.urls),
    # ]

    "ROLES": {
        "admin": "/dashboard/admin/",
        "user": "/dashboard/",
    },
    # make sure it matches your models.py roles
    # ROLE_CHOICES = [
    #     ('admin', 'Administrator'),
    #     ('user', 'Regular User'),
    # ]

    "DENY_BEHAVIOR": "redirect",  # or "forbidden"
}

# Admin security
MIDDLEWARE.insert(0, 'django_did_auth.security.admin.ipwhitelist.AdminIPWhitelistMiddleware')

```

- Default DID_AUTH config (can be overridden in dev/prod):

```python
DID_AUTH = {
    # "LOGIN_REDIRECT": "/dashboard/", # already redirect based on roles below
    "LOGOUT_REDIRECT": "/login/",
    "ADMIN_URL": "admin/",
    "ADMIN_IP_WHITELIST": ['127.0.0.1', '::1'],  # Localhost by default

    "ROLES": {
        "admin": "/admin-dashboard/",
        "staff": "/staff-dashboard/",
        "moderator": "/moderator-dashboard/",
        "user": "/dashboard/",
    },
    "DENY_BEHAVIOR": "redirect",  # or "forbidden"

    "EMAIL": {
        "VERIFY_EXPIRY_HOURS": 24,
        "RESET_EXPIRY_HOURS": 1,
        "FROM_EMAIL": None,  # Will use DEFAULT_FROM_EMAIL
    },

    "RATE_LIMIT": {
        "LOGIN": "10/m",
        "REGISTER": "5/m",
        "PASSWORD_RESET": "5/m",
    },

    "UI_FRAMEWORK": "tailwind",  # "tailwind" or "bootstrap"

    "ENABLE_AUDIT": True,
    "TRUST_PROXY": False,
    
    "SECURITY": {
        "PASSWORD_MIN_LENGTH": 12,
        "ENABLE_AXES": True,
        "LOCKOUT_AFTER_ATTEMPTS": 5,
        "LOCKOUT_DURATION_MINUTES": 30,
        "REQUIRE_HTTPS": True,          # Enforce in production
    },
    "AUDIT": {
        "ENABLED": True,
        "LOG_SENSITIVE": False,         # Don't log passwords
    }
    
}
```

---

## 🔐 Security Configuration (MANDATORY)

### Password Hashing

```python
# --------------------------------------------------
# 🔑 PASSWORD HASHERS (UPGRADE)
# --------------------------------------------------
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # 🔥 strongest
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

---

### Rate Limiting (Redis)

```python
# --------------------------------------------------
#  🔐 AUTHENTICATION BACKENDS & RATE LIMITING
# --------------------------------------------------
# Rate limiting (for login/register)
RATELIMIT_VIEW = 'ratelimit.views.RatelimitView'
RATELIMIT_USE_CACHE = 'default'
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# --------------------------------------------------
# 🗄️ CACHE (Required for django-ratelimit)
# --------------------------------------------------
REDIS_REQUIRED = os.getenv("REDIS_REQUIRED", "False").lower() == "true"
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1')
if REDIS_REQUIRED and not DEBUG:
    if not REDIS_URL:
        raise ValueError("❌ REDIS_URL required in production")
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,
    }
}

# --------------------------------------------------
# 🔴 Runtime Redis Health Check (IMPORTANT)
# --------------------------------------------------
if REDIS_REQUIRED and not DEBUG:
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        conn.ping()
    except Exception as e:
        raise Exception(f"❌ Redis not reachable: {e}")

```

---

### Axes Protection

```python

MIDDLEWARE += [
    'axes.middleware.AxesMiddleware',
]

# --------------------------------------------------
# 🔐 AXES HARDENING (ALIGNED)
# --------------------------------------------------
# Axes fallback behavior
# False = Fail Closed (secure) | app becomes unusable if Redis is down → recommended for maximum security in production
# True = Fail Open (usable) | app continues but reduced security (no rate limiting, no lockouts) → use only if you have a reliable Redis connection in production
AXES_FAIL_SILENTLY = True if DEBUG else False
# AXES_ENABLED = True
AXES_ENABLED = True if REDIS_REQUIRED else DEBUG
AXES_VERBOSE = True # (optional) Log lockouts with more detail (check logs → you’ll see exactly why login fails)
AXES_CACHE = 'default'
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 30
AXES_RESET_ON_SUCCESS = True
AXES_USERNAME_FORM_FIELD = 'email'
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']
# Optional UI override
AXES_LOCKOUT_TEMPLATE = 'did_auth/lockout.html'
```

### Email Settings
```python
# --------------------------------------------------
# 📧 EMAIL CONFIGURATION
# --------------------------------------------------
EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend'
    if DEBUG else
    'django.core.mail.backends.smtp.EmailBackend'
)

EMAIL_HOST = os.getenv("EMAIL_HOST")

if not DEBUG and not EMAIL_HOST:
    raise ValueError("❌ EMAIL_HOST must be set in production")

EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

```

### Logging settings (extend existing logging)

```python
# --------------------------------------------------
# 🧾 LOGGING (EXTENDED FOR DID_AUTH)
# --------------------------------------------------
LOGGING['loggers'].update({
    'did_auth.audit': {
        'handlers': ['console', 'security_file'],
        'level': 'INFO',
        'propagate': False,
    },
    'did_auth.app': {
        'handlers': ['console', 'app_file'],
        'level': 'INFO',
        'propagate': False,
    },
    'did_auth.ratelimit': {
        'handlers': ['console', 'security_file'],
        'level': 'WARNING',
        'propagate': False,
    },
})
```

---

## 🧠 Role-Based Redirection (already in #3 Required Settings)

```python
DID_AUTH = {
    "ROLES": {
        "admin": "/dashboard/admin/",
        "staff": "/dashboard/staff/",
        "user": "/dashboard/",
    }
}
```

---

## 📧 Email Integration
- you can use in your project the email sending function using:

```python
from django_did_auth.core.flows.email_flow import send_general_email

send_general_email(
    request,
    user,
    "Welcome!",
    "emails/welcome.html",
    {"name": user.first_name}
)
```

create the `templates/emails/welcome.html`

---

## 🧾 Audit Logging
- to use the audit log feature inside your project:

```python
from django_did_auth.security.audit.logger import log_event

log_event(request, "login_success", user=request.user)

log_event(
    request=None,
    event="manual_test_error",
    level="error",
    extra={"info": "testing"}
)
```

## Templates Overiding

Create the following files:
- `templates/did_auth/login.html`
```html
<form method="post" class="space-y-6">
    {% csrf_token %}
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
        {{ form.email }}
        {% if form.email.errors %}
            <p class="mt-1 text-red-500 text-sm">{{ form.email.errors.0 }}</p>
        {% endif %}
    </div>
    <div>
        <div class="flex justify-between items-center">
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <a href="{% url 'did_auth:password_reset_request' %}" class="text-sm text-blue-600 hover:text-blue-500">Forgot password?</a>
        </div>
        {{ form.password }}
        {% if form.password.errors %}
            <p class="mt-1 text-red-500 text-sm">{{ form.password.errors.0 }}</p>
        {% endif %}
    </div>
    <button type="submit"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 rounded-2xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
        Sign in
    </button>
</form>
```
- `templates/did_auth/register.html`
```html
<form method="post" class="space-y-6">
    {% csrf_token %}
    <div class="grid grid-cols-2 gap-4">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">First name</label>
            {{ form.first_name }}
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Last name</label>
            {{ form.last_name }}
        </div>
    </div>
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
        {{ form.email }}
    </div>
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
        {{ form.password1 }}
    </div>
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Confirm password</label>
        {{ form.password2 }}
    </div>
    <button type="submit"
            class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 rounded-2xl transition-all duration-200">
        Create account
    </button>
</form>
```
- `templates/did_auth/lockout.html`
```html
<div class="text-center py-12 space-y-6">
    <h2 class="text-3xl font-bold text-red-600">Account Temporarily Locked</h2>
    <p class="text-gray-600">Too many failed login attempts from this IP or account.</p>
    <p>Please try again later or contact support.</p>
    
    <a href="{% url 'did_auth:login' %}" 
       class="inline-block px-6 py-3 bg-gray-800 text-white rounded-2xl hover:bg-gray-900">
        Back to Login
    </a>
</div>
```
- `templates/did_auth/password_reset_confirm.html`
```html
{% if valid_link and form %}
    <form method="post" class="space-y-6">
        {% csrf_token %}
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">New password</label>
            {{ form.new_password }}
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirm new password</label>
            {{ form.confirm_password }}
        </div>
        <button type="submit"
                class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3.5 rounded-2xl">
            Reset password
        </button>
    </form>
{% else %}
    <div class="text-center text-red-600 py-8">
        This password reset link is invalid or has expired.
    </div>
    <a href="{% url 'did_auth:password_reset_request' %}" 
        class="block text-center text-blue-600 hover:text-blue-500">
        Request a new reset link
    </a>
{% endif %}
```
- `templates/did_auth/password_reset_request.html`
```html
<form method="post" class="space-y-6">
    {% csrf_token %}
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
        {{ form.email }}
    </div>
    <button type="submit"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 rounded-2xl transition-all">
        Send reset link
    </button>
</form>
```
- `templates/did_auth/verification_sent.html`
```html
<h2 class="text-3xl font-semibold text-gray-900">Check your email</h2>
<p class="text-gray-600 max-w-sm mx-auto">
    We've sent a verification link to your email address. 
    Please click the link to activate your account.
</p>
```
- `templates/did_auth/email/activation.html`
```html
<h2>Hi {{ user.first_name|default:user.email }},</h2>
<p>Thank you for registering! Please click the button below to activate your account:</p>
<a href="{{ activation_link }}" 
    style="display: inline-block; background: #4f46e5; color: white; padding: 14px 28px; 
            text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0;">
    Activate My Account
</a>
<p style="color: #666; font-size: 0.95rem;">
    This link will expire in {{ expiry|default:24 }} hours.
</p>
```
- `templates/did_auth/email/password_reset.html`
```html
<h2>Hi {{ user.first_name|default:user.email }},</h2>
<p>You requested a password reset. Click the link below to set a new password:</p>
<a href="{{ reset_link }}" 
    style="display: inline-block; background: #4f46e5; color: white; padding: 14px 28px; 
            text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0;">
    Reset My Password
</a>
<p style="color: #666;">This link will expire soon.</p>
<p>If you didn't request this, please ignore this email.</p>
```
- `templates/profile/change_password.html`
```html
<form method="post">
    {% csrf_token %}
    {{ form.non_field_errors }}
    <div class="space-y-4">
        {{ form.current_password.label_tag }}
        {{ form.current_password }}

        {{ form.new_password.label_tag }}
        {{ form.new_password }}

        {{ form.confirm_password.label_tag }}
        {{ form.confirm_password }}
    </div>
    <button class="mt-6 w-full bg-blue-600 text-white py-2 rounded">
        Update Password
    </button>
</form>
```

---

## Sample custom model
- `your_project/users/models.py`

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra_fields)
class CustomUser(AbstractUser):
    username = None
    # Role choices (easy to extend)
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),
        ('moderator', 'Moderator'),
        ('user', 'Regular User'),
    ]
    # Core fields
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    # Role & profile
    role = models.CharField(
        _('role'), 
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user',
        db_index=True
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Will be False until email verified
    date_joined = models.DateTimeField(default=timezone.now)
    activation_token_created = models.DateTimeField(
        _('activation token created'),
        null=True,
        blank=True
    )
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    def __str__(self):
        return self.email
```

## Re-used Register flow on your `Views`
```python
from django_did_auth.core.flows.register_flow import register_user

if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            user = register_user(request, form)
```
- this will save as `user.is_active = False`


## Role-aware Access Control

```python
from django_did_auth.security.decorators.roles import role_required

@role_required("owner") # Supported: @role_required("admin", "owner")
def dashboard(request):
    ...
```
If user is:
- ✅ owner → allow
- ❌ not owner → redirect or forbidden
if you have `DID_AUTH["DENY_BEHAVIOR"] = "redirect",` in settings it redirect to their dashboard, if `DID_AUTH["DENY_BEHAVIOR"] = "forbidden",` in setting it show error 403 instead

---

# How to use handler404

## In PROJECT `urls.py`
```python
handler404 = "django_did_auth.core.utils.errors.handle_404"
```

---

# Overried Error Templates

## Template override only
Create the following templates
- `Templates/did_auth/errors/401.html`

```html
<div class="bg-white shadow-lg rounded-2xl p-8 max-w-md text-center">
    <div class="text-red-500 text-6xl font-bold">401</div>
    <h1 class="text-2xl font-semibold mt-4 text-gray-800">
        Authentication Required
    </h1>
    <p class="text-gray-600 mt-2">
       {{ message|default:"You do not have permission." }}
    </p>
    <p class="text-sm text-gray-400 mt-3">
        If you believe this is an error, contact your administrator.
    </p>
    <a href="/" 
       class="inline-block mt-6 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Go Home
    </a>
</div>
```
- `Templates/did_auth/errors/403.html`

```html
<div class="bg-white shadow-lg rounded-2xl p-8 max-w-md text-center">
    <div class="text-red-500 text-6xl font-bold">Error 403</div>
    <h1 class="text-2xl font-semibold mt-4 text-gray-800">
        Access Denied
    </h1>
    <p class="text-gray-600 mt-2">
       {{ message|default:"You do not have permission." }}
    </p>
    <p class="text-sm text-gray-400 mt-3">
        If you believe this is an error, contact your administrator.
    </p>
    <a href="/" 
       class="inline-block mt-6 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Go Home
    </a>
</div>
```
- `Templates/did_auth/errors/404.html`

```html
<div class="bg-white shadow-lg rounded-2xl p-8 max-w-md text-center">
    <div class="text-red-500 text-6xl font-bold">404</div>
    <h1 class="text-2xl font-semibold mt-4 text-gray-800">
        Page Not Found
    </h1>
    <p class="text-gray-600 mt-2">
       {{ message|default:"You do not have permission." }}
    </p>
    <p class="text-sm text-gray-400 mt-3">
        If you believe this is an error, contact your administrator.
    </p>
    <a href="/" 
       class="inline-block mt-6 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Go Home
    </a>
</div>
```
- `Templates/did_auth/errors/423.html`

```html
<div class="bg-white shadow-lg rounded-2xl p-8 max-w-md text-center">
    <div class="text-red-500 text-6xl font-bold">423</div>
    <h1 class="text-2xl font-semibold mt-4 text-gray-800">
        Account Locked
    </h1>
    <p class="text-gray-600 mt-2">
       {{ message|default:"You do not have permission." }}
    </p>
    <p class="text-sm text-gray-400 mt-3">
        If you believe this is an error, contact your administrator.
    </p>
    <a href="/" 
       class="inline-block mt-6 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Go Home
    </a>
</div>
```
- `Templates/did_auth/errors/429.html`

```html
<div class="bg-white shadow-lg rounded-2xl p-8 max-w-md text-center">
    <div class="text-red-500 text-6xl font-bold">429</div>
    <h1 class="text-2xl font-semibold mt-4 text-gray-800">
        Too Many Requests
    </h1>
    <p class="text-gray-600 mt-2">
       {{ message|default:"You do not have permission." }}
    </p>
    <p class="text-sm text-gray-400 mt-3">
        If you believe this is an error, contact your administrator.
    </p>
    <a href="/" 
       class="inline-block mt-6 px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Go Home
    </a>
</div>
```


## Other overried technuiqes 
If you don't want to create/overide the html above, in `templates/did_auth/errors/`, then use the approach below:

- Add in `settings.py` (SETTINGS — PLUGGABLE OVERRIDE)

```python
DID_AUTH["ERROR_HANDLERS"] = {
        "403": "myproject.errors.custom_403",
        "404": "myproject.errors.custom_404",
        "429": "myproject.errors.custom_429",
    }
```

- PROJECT OVERRIDE EXAMPLE (`myproject/errors.py`)
```python
from django.shortcuts import render

def custom_403(request, message=None):
    return render(request, "custom/403.html", {"message": message}, status=403)
```

How it works
```bash
role_required()
    ↓
handle_403()
    ↓
check settings.DID_AUTH["ERROR_HANDLERS"]["403"]
    ↓
IF exists → use project function
ELSE → fallback to framework default
```

## How to use error handling in project
- example: `my_project/app_name/views.py`
```python

from django_did_auth.core.utils.errors import handle_error

return handle_error(request, 403, "You are not allowed to access this page.")
return handle_error(request, 429, "Too many attempts. Please try again later.")
return handle_error(request, 401, "Please login first.")

```

- A) Role-based dashboard
```python
@login_required
def staff_dashboard_view(request):

    if request.user.role != "staff":
        return handle_error(request, 403, "Staff access only.")

    return render(request, "staff/dashboard.html")
```
- B) Profile ownership
```python
def profile_view(request, user_id):

    if request.user.id != user_id:
        return handle_error(request, 403, "You cannot view this profile.")

    ...
```
- C) API-style auth check
```python
def api_view(request):

    if not request.user.is_authenticated:
        return handle_error(request, 401, "Authentication required.")

    ...
```
- Object not found (manual 404)
```python
obj = MyModel.objects.filter(id=pk).first()

if not obj:
    return handle_error(request, 404, "Item not found.")
```


---

## 🚨 Production Checklist

- [ ] DEBUG=False
- [ ] HTTPS enabled
- [ ] Redis running
- [ ] Strong SECRET_KEY
- [ ] Secure cookies enabled
- [ ] CSP enabled
- [ ] Email configured
- [ ] Admin URL changed

---

## 🔌 Extensibility

- Custom templates override
- Hook system (pre/post auth)
- Future MFA integration ready

---


## 🧠 Recommended Additions

- MFA → django-otp
- CAPTCHA → django-simple-captcha
- SSO → OAuth2 / OpenID

---

## 📜 License

MIT
