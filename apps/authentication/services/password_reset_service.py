import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetService:
    """منطق بازیابی رمز عبور"""

    @staticmethod
    def build_reset_link(user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        base = settings.FRONTEND_URL.rstrip('/')
        return f'{base}/reset-password?uid={uid}&token={token}'

    @classmethod
    def send_reset_email(cls, user):
        link = cls.build_reset_link(user)
        minutes = settings.PASSWORD_RESET_TIMEOUT // 60
        body = (
            'سلام،\n\n'
            'درخواست بازیابی رمز عبور برای حساب شما ثبت شد. '
            'برای تعیین رمز جدید روی لینک زیر کلیک کنید:\n\n'
            f'{link}\n\n'
            f'این لینک {minutes} دقیقه معتبر است. '
            'اگر شما این درخواست را نداده‌اید، این ایمیل را نادیده بگیرید؛ '
            'رمز عبور شما تغییری نمی‌کند.'
        )
        send_mail(
            subject='بازیابی رمز عبور',
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    @classmethod
    def request_reset(cls, email):
        """
        اگر کاربر فعالی با این ایمیل باشد، لینک بازیابی می‌فرستد.
        خطای ارسال ایمیل فقط لاگ می‌شود تا وجود یا نبود حساب لو نرود.
        """
        for user in User.objects.filter(email__iexact=email, is_active=True):
            try:
                cls.send_reset_email(user)
            except Exception:
                logger.exception('Failed to send password reset email (user id=%s)', user.pk)

    @staticmethod
    def reset_password(user, new_password):
        user.set_password(new_password)
        user.save(update_fields=['password'])

        # همهٔ refresh tokenهای قبلی باطل شوند
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)
