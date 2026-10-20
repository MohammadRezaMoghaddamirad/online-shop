from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.validators import normalize_email

User = get_user_model()


class ForgotPasswordSerializer(serializers.Serializer):
    """درخواست لینک بازیابی رمز عبور"""
    email = serializers.EmailField(max_length=150)

    def validate_email(self, value):
        return normalize_email(value)


class ResetPasswordSerializer(serializers.Serializer):
    """تعیین رمز جدید با id کاربر و توکن دریافتی از ایمیل"""
    id = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self._get_user(attrs['id'])
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
    def _get_user(user_id):
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, DjangoValidationError, User.DoesNotExist):
            return None
