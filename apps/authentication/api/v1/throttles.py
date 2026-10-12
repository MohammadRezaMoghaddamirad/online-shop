from rest_framework.throttling import SimpleRateThrottle


class _IPRateThrottle(SimpleRateThrottle):
    """محدودیت بر اساس IP (برای کاربر لاگین‌شده و مهمان یکسان)."""

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class ForgotPasswordThrottle(_IPRateThrottle):
    scope = 'forgot_password'
    rate = '5/hour'


class ResetPasswordThrottle(_IPRateThrottle):
    scope = 'reset_password'
    rate = '10/hour'
