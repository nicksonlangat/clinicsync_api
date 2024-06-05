from rest_framework import permissions


class IsOwnerPermission(permissions.BasePermission):
    """
    Allows access only to authenticated, with-owner-role users.
    """

    # message = "User must have an owner role"

    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and request.user.role == "Owner"
        )
