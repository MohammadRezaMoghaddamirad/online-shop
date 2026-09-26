from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """ÙÙ‚Ø· Ø§Ø¯Ù…ÛŒÙ†"""
    message = 'ÙÙ‚Ø· Ù…Ø¯ÛŒØ±Ø§Ù† Ø¯Ø³ØªØ±Ø³ÛŒ Ø¯Ø§Ø±Ù†Ø¯.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == 'admin')
        )
