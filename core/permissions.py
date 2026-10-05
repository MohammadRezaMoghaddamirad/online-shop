from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """فقط مدیر فروشگاه (role=admin)."""

    message = "فقط مدیر فروشگاه به این بخش دسترسی دارد."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_shop_admin)


class IsCustomer(BasePermission):
    """فقط مشتری عادی (role=customer)."""

    message = "این بخش مخصوص مشتریان است."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_customer)


class IsOwner(BasePermission):
    """دسترسی به آبجکت فقط برای صاحب آن (فیلد user)."""

    message = "شما فقط به اطلاعات خودتان دسترسی دارید."

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == request.user.id
