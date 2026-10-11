class TokenService:
    """سرویس تولید و مدیریت توکن‌ها — با import تعویقی"""

    @staticmethod
    def generate_tokens_for_user(user):
        """تولید توکن Access و Refresh برای کاربر"""
        # ✅ import داخل تابع
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def blacklist_token(refresh_token):
        """blacklist کردن Refresh Token"""
        try:
            # ✅ import داخل تابع
            from rest_framework_simplejwt.tokens import RefreshToken

            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            return False