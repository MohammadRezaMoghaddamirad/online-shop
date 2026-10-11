from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """خواندن برای همه، نوشتن فقط ادمین"""
    message = 'فقط مدیران می‌توانند تغییرات اعمال کنند.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == 'admin')
        )
