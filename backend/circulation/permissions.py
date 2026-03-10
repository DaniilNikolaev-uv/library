from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import Role


class IsStaff(BasePermission):
    """Только admin или librarian."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (Role.ADMIN, Role.LIBRARIAN)


class IsStaffOrOwner(BasePermission):
    """
    Сотрудник — полный доступ.
    Читатель — только свои выдачи (для list/retrieve).
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role in (Role.ADMIN, Role.LIBRARIAN):
            return True
        # Читатель видит только свои выдачи
        try:
            return obj.reader.user_id == request.user.pk
        except Exception:
            return False
