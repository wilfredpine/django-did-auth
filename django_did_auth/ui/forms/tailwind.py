"""
Tailwind CSS styled forms for django_did_auth.
Clean, modern, and production-ready.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

# Reusable Tailwind input classes
TAILWIND_INPUT = (
    "w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm "
    "focus:ring-2 focus:ring-blue-600 focus:border-blue-600 focus:outline-none "
    "transition-all duration-200 text-gray-900 placeholder-gray-400"
)

TAILWIND_LABEL = "block text-sm font-medium text-gray-700 mb-1"


class RegistrationForm(UserCreationForm):
    """Registration form with Tailwind styling"""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'you@example.com',
            'autocomplete': 'email'
        }),
        label=_('Email address'),
        required=True,
        help_text=_('A verification email will be sent to this address.')
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'First name'
        }),
        label=_('First name'),
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Last name'
        }),
        label=_('Last name'),
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': TAILWIND_INPUT,
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': TAILWIND_INPUT,
            'placeholder': 'Confirm password'
        })
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Confirm password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Require email verification
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Login form - Email + Password"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'you@example.com',
            'autocomplete': 'email'
        }),
        label=_('Email address')
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        }),
        label=_('Password')
    )


class PasswordResetRequestForm(forms.Form):
    """Request password reset link"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'you@example.com',
            'autocomplete': 'email'
        }),
        label=_('Email address'),
        required=True
    )


class SetNewPasswordForm(forms.Form):
    """Set new password after reset link"""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'New password',
            'autocomplete': 'new-password'
        }),
        label=_('New password'),
        required=True,
        min_length=12
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        }),
        label=_('Confirm new password'),
        required=True
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(_("The two passwords do not match."))
        return cleaned_data


class ResendVerificationForm(forms.Form):
    """Resend verification email"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'you@example.com'
        }),
        label=_('Email address'),
        required=True
    )


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Current password',
            'autocomplete': 'current-password'
        }),
        label=_('Current password'),
        required=True
    )
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'New password',
            'autocomplete': 'new-password'
        }),
        label=_('New password'),
        required=True,
        min_length=12
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        }),
        label=_('Confirm new password'),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        if not self.user.check_password(self.cleaned_data.get('current_password')):
            raise ValidationError("Current password is incorrect.")
        return self.cleaned_data.get('current_password')

    def clean(self):
        cleaned_data = super().clean()
        new = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")

        if new != confirm:
            raise ValidationError("Passwords do not match.")

        validate_password(new, self.user)
        return cleaned_data