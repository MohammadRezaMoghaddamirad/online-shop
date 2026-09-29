from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny


class LoginView(TokenObtainPairView):
    """ÙˆØ±ÙˆØ¯ Ú©Ø§Ø±Ø¨Ø± â€” Ø¯Ø±ÛŒØ§ÙØª Access Ùˆ Refresh Token"""
    permission_classes = [AllowAny]
