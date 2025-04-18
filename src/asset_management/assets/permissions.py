from rest_framework import permissions


class IsQAUser(permissions.BasePermission):
    """
    Custom permission to only allow users with QA role to access QA-related endpoints.
    """

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.role == "qa"
        )


class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to only allow admin users or managers to access certain endpoints.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == "manager")
        )
