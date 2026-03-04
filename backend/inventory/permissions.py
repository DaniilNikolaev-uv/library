from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrLibrarian(BasePermission):
    """
    Чтение — любой аутентифицированный.
    Запись — только сотрудники (у кого есть related Staff).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return hasattr(request.user, "staff")
