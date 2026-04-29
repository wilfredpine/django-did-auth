def on_login_success(request, user):
    """Override in project if needed"""
    pass

def on_register(user):
    pass

def on_logout(request):
    """Hook called after logout"""
    pass