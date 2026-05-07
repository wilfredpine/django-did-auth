from rest_framework.permissions import BasePermission

def role_access(*allowed_roles):
    """
    Factory that returns a DRF permission class
    
    Usage:
        
        from rest_framework.permissions import IsAuthenticated
        from django_did_auth.api.permissions import role_access

        class UserOnlyAPIView(APIView):
            permission_classes = [IsAuthenticated, role_access('user')]

            def get(self, request):
                return Response({"message": "User access granted"})
                
    Multiple roles supported: 
               
        permission_classes = [IsAuthenticated, role_access('admin', 'staff')]
    """
    class RolePermission(BasePermission):
        message = "You do not have permission to access this resource."

        def has_permission(self, request, view):
            user = request.user

            if not user or not user.is_authenticated:
                return False
            
            if user.is_superuser:
                return True

            if not hasattr(user, "role"):
                return False

            return str(user.role).lower() in [
                str(r).lower() for r in allowed_roles
            ]

    return RolePermission