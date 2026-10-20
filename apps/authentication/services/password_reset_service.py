import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetService:
    """منطق بازیابی رمز عبور"""

    @staticmethod
    def generate_token(user):
        """id کاربر و token بازیابی را می‌سازد."""
        token = default_token_generator.make_token(user)
        return user.pk, token

    @classmethod
    def build_reset_link(cls, user):
        user_id, token = cls.generate_token(user)
        base = settings.FRONTEND_URL.rstrip('/')
        return f'{base}/reset-password?id={user_id}&token={token}'

    @classmethod
    def notify_user(cls, user, user_id, token):
        """
        TODO: وقتی بخش نوتیفیکیشن آماده شد، اینجا برای کاربر ارسال شود.
        فعلاً فقط توکن ساخته می‌شود و هیچ پیامی ارسال نمی‌شود.
        """
        if settings.DEBUG:
            # فقط برای تست در محیط توسعه؛ توکن هرگز در پاسخ API برنمی‌گردد
            logger.debug('Password reset token (user id=%s): token=%s', user_id, token)

    @classmethod
    def request_reset(cls, email):
        """
        اگر کاربر فعالی با این ایمیل باشد، توکن بازیابی ساخته می‌شود.
        خطاها فقط لاگ می‌شوند تا وجود یا نبود حساب لو نرود.
        """
        for user in User.objects.filter(email__iexact=email, is_active=True):
            try:
                user_id, token = cls.generate_token(user)
                cls.notify_user(user, user_id, token)
            except Exception:
                logger.exception('Failed to generate password reset token (user id=%s)', user.pk)

    @staticmethod
    def reset_password(user, new_password):
        user.set_password(new_password)
        user.save(update_fields=['password'])

        # همهٔ refresh tokenهای قبلی باطل شوند
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
