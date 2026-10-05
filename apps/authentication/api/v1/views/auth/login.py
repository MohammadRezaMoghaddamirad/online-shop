from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


@extend_schema(
    tags=['احراز هویت'],
    summary='ورود کاربر',
    description='با وارد کردن نام کاربری و رمز عبور، توکن دسترسی و توکن تازه‌سازی دریافت کنید.',
    request=inline_serializer(
        name='LoginRequest',
        fields={
            'username': serializers.CharField(help_text='نام کاربری'),
            'password': serializers.CharField(help_text='رمز عبور'),
        },
    ),
    responses={
        200: inline_serializer(
            name='LoginResponse',
            fields={
                'refresh': serializers.CharField(help_text='توکن تازه‌سازی'),
                'access': serializers.CharField(help_text='توکن دسترسی'),
            },
        ),
        401: inline_serializer(
            name='LoginErrorResponse',
            fields={'detail': serializers.CharField(help_text='پیام خطا')},
        ),
    },
)
class LoginView(TokenObtainPairView):
    """ورود کاربر و دریافت توکن‌ها"""
    permission_classes = [AllowAny]