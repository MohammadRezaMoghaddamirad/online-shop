from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..services.token_service import TokenService


class LogoutView(generics.GenericAPIView):
    """Ø®Ø±ÙˆØ¬ Ú©Ø§Ø±Ø¨Ø± â€” blacklist Ú©Ø±Ø¯Ù† Refresh Token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'ÙÛŒÙ„Ø¯ refresh Ù„Ø§Ø²Ù… Ø§Ø³Øª.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if TokenService.blacklist_token(refresh_token):
            return Response(
                {'detail': 'Ø®Ø±ÙˆØ¬ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø§Ù†Ø¬Ø§Ù… Ø´Ø¯.'},
                status=status.HTTP_205_RESET_CONTENT
            )
        return Response(
            {'detail': 'ØªÙˆÚ©Ù† Ù†Ø§Ù…Ø¹ØªØ¨Ø± Ø§Ø³Øª.'},
            status=status.HTTP_400_BAD_REQUEST
        )
