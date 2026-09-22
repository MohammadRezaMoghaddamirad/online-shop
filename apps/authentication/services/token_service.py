from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:
    """Ø³Ø±ÙˆÛŒØ³ Ù…Ø¯ÛŒØ±ÛŒØª ØªÙˆÚ©Ù†â€ŒÙ‡Ø§"""

    @staticmethod
    def generate_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def blacklist_token(refresh_token_str):
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
            return True
        except Exception:
            return False
