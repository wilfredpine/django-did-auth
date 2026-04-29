# 🔐 django-sauth

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
#  🔐 AUTHENTICATION & SAUTH CONFIG
# --------------------------------------------------
INSTALLED_APPS += [
    'django_sauth', # install here
    'axes', 
    'django_ratelimit',
    'users', # apps for custom user model
]
```

---

### 2. URLs

```python
urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # SAUTH URLs
    path('auth/', include('django_sauth.urls')), # Include SAUTH URLs

    # 👤 Role Dashboards
    path('dashboard/admin/', main_views.admin_dashboard),
    path('dashboard/', main_views.user_dashboard),
]
```

---

### 3. Required Settings

```python
AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = 'sauth:login'

SAUTH = {
    "LOGIN_REDIRECT": "/dashboard/",
    "LOGOUT_REDIRECT": "/auth/login/",
    "ROLES": {
        "admin": "/dashboard/admin/",
        "user": "/dashboard/",
    },
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
AXES_LOCKOUT_TEMPLATE = 'sauth/lockout.html'
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
# 🧾 LOGGING (EXTENDED FOR SAUTH)
# --------------------------------------------------
LOGGING['loggers'].update({
    'sauth.audit': {
        'handlers': ['console', 'security_file'],
        'level': 'INFO',
        'propagate': False,
    },
    'sauth.app': {
        'handlers': ['console', 'app_file'],
        'level': 'INFO',
        'propagate': False,
    },
    'sauth.ratelimit': {
        'handlers': ['console', 'security_file'],
        'level': 'WARNING',
        'propagate': False,
    },
})
```

---

## 🧠 Role-Based Redirection (already in #3 Required Settings)

```python
SAUTH = {
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
from django_sauth.core.flows.email_flow import send_general_email

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
from django_sauth.security.audit.logger import log_event

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
- `templates/sauth/login.html`
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
            <a href="{% url 'sauth:password_reset_request' %}" class="text-sm text-blue-600 hover:text-blue-500">Forgot password?</a>
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
- `templates/sauth/register.html`
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
- `templates/sauth/lockout.html`
```html
<div class="text-center py-12 space-y-6">
    <h2 class="text-3xl font-bold text-red-600">Account Temporarily Locked</h2>
    <p class="text-gray-600">Too many failed login attempts from this IP or account.</p>
    <p>Please try again later or contact support.</p>
    
    <a href="{% url 'sauth:login' %}" 
       class="inline-block px-6 py-3 bg-gray-800 text-white rounded-2xl hover:bg-gray-900">
        Back to Login
    </a>
</div>
```
- `templates/sauth/password_reset_confirm.html`
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
    <a href="{% url 'sauth:password_reset_request' %}" 
        class="block text-center text-blue-600 hover:text-blue-500">
        Request a new reset link
    </a>
{% endif %}
```
- `templates/sauth/password_reset_request.html`
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
- `templates/sauth/verification_sent.html`
```html
<h2 class="text-3xl font-semibold text-gray-900">Check your email</h2>
<p class="text-gray-600 max-w-sm mx-auto">
    We've sent a verification link to your email address. 
    Please click the link to activate your account.
</p>
```
- `templates/sauth/email/activation.html`
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
- `templates/sauth/email/password_reset.html`
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

---

## Sample custom model
- `your_project/users/models.py`

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
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
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    def __str__(self):
        return self.email
```

## Re-used Register flow
```python
from django_sauth.core.flows.register_flow import register_user

if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid():
            user = register_user(request, form)
```
- it save as `user.is_active = False`


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

## 🧱 Architecture

```
django_sauth/
├── core/
├── security/
├── flows/
├── templates/
```

---

## 🧠 Recommended Additions

- MFA → django-otp
- CAPTCHA → django-simple-captcha
- SSO → OAuth2 / OpenID

---

## 📜 License

MIT
