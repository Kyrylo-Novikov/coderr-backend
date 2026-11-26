from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsBusinessUserOrReadOnly(BasePermission):
    """
    Allows safe methods for all users, while only business users have the permission to use other methods
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.type == 'business'


class IsOwner(BasePermission):
    """
    Allows safe methods for every user and write methods only for the creator of the offer.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
