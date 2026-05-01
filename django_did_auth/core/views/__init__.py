from .register import register_view
from .login import login_view
from .logout import logout_view
from .activation import activate_account_view
from .password_reset import password_reset_request_view, password_reset_confirm_view
from .password import change_password_view
__all__ = [
    'register_view', 'login_view', 'logout_view',
    'activate_account_view', 'password_reset_request_view',
    'password_reset_confirm_view', 'change_password_view'
]