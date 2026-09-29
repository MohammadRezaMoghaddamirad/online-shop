from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """فقط ادمین"""
    message = 'فقط مدیران دسترسی دارند.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == 'admin')
        )