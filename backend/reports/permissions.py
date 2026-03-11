from rest_framework.permissions import BasePermission

from accounts.models import Role


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.ADMIN, Role.LIBRARIAN)
        )

