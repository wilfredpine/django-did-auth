from django.contrib.auth import authenticate

def authenticate_user(request, email, password):
    return authenticate(request, username=email, password=password)