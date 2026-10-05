from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers


@extend_schema(
    tags=['احراز هویت'],
    summary='تمدید توکن دسترسی',
    description='با ارسال توکن تازه‌سازی معتبر، یک توکن دسترسی جدید دریافت کنید.',
    request=inline_serializer(
        name='TokenRefreshRequest',
        fields={
            'refresh': serializers.CharField(help_text='توکن تازه‌سازی معتبر'),
        },
    ),
    responses={
        200: inline_serializer(
            name='TokenRefreshResponse',
            fields={
                'access': serializers.CharField(help_text='توکن دسترسی جدید'),
            },
        ),
        401: inline_serializer(
            name='TokenRefreshErrorResponse',
            fields={'detail': serializers.CharField(help_text='پیام خطا')},
        ),
    },
)
class TokenRefreshCustomView(TokenRefreshView):
    """تمدید توکن دسترسی"""
    permission_classes = [AllowAny]