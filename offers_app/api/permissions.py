from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessUserOrReadOnly(BasePermission):
    """
    Allows safe methods for all users, while only business users have the permission to use other methods 
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.type == 'business'
