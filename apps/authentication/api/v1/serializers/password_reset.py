from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

User = get_user_model()


class ForgotPasswordSerializer(serializers.Serializer):
    """درخواست لینک بازیابی رمز عبور"""
    email = serializers.EmailField(max_length=150)

    def validate_email(self, value):
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    """تعیین رمز جدید با uid و توکن دریافتی از ایمیل"""
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self._get_user(attrs['uid'])
        if user is None or not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError(
                {'token': 'لینک بازیابی نامعتبر است یا منقضی شده است.'}
            )
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'رمزهای عبور یکسان نیستند.'}
            )
        try:
            validate_password(attrs['password'], user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        attrs['user'] = user
        return attrs

    @staticmethod
    def _get_user(uidb64):
        try:
            pk = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=pk, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
