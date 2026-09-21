from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """فقط ادمین‌ها دسترسی دارند"""
    message = 'فقط مدیران دسترسی دارند.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == 'admin')
        )


class IsOwnerOrAdmin(BasePermission):
    """فقط صاحب شیء یا ادمین"""
    message = 'شما به این منبع دسترسی ندارید.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        return obj == request.user