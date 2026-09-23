from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Ø®ÙˆØ§Ù†Ø¯Ù† Ø¨Ø±Ø§ÛŒ Ù‡Ù…Ù‡ØŒ Ù†ÙˆØ´ØªÙ† ÙÙ‚Ø· Ø§Ø¯Ù…ÛŒÙ†"""
    message = 'ÙÙ‚Ø· Ù…Ø¯ÛŒØ±Ø§Ù† Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ù†Ø¯ ØªØºÛŒÛŒØ±Ø§Øª Ø§Ø¹Ù…Ø§Ù„ Ú©Ù†Ù†Ø¯.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == 'admin')
        )
