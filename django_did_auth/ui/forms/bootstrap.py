"""
Bootstrap 5 styled forms for django_did_auth.
Use when DID_AUTH["UI_FRAMEWORK"] = "bootstrap"
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationForm(UserCreationForm):
    """Bootstrap 5 Registration Form"""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autocomplete': 'email'
        }),
        label=_('Email address'),
        required=True,
        help_text=_('A verification email will be sent to this address.')
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        }),
        label=_('First name'),
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
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
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Confirm password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Bootstrap Login Form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com'
        }),
        label=_('Email address')
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label=_('Password')
    )


class PasswordResetRequestForm(forms.Form):
    """Bootstrap Password Reset Request"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com'
        }),
        label=_('Email address'),
        required=True
    )


class SetNewPasswordForm(forms.Form):
    """Bootstrap Set New Password"""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        }),
        label=_('New password'),
        required=True,
        min_length=12
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
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
    """Bootstrap Resend Verification"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com'
        }),
        label=_('Email address'),
        required=True
    )