from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.api.v1.serializers import (
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from apps.authentication.api.v1.throttles import (
    ForgotPasswordThrottle,
    ResetPasswordThrottle,
)
from apps.authentication.services.password_reset_service import PasswordResetService

MessageResponse = inline_serializer(
    name='PasswordMessageResponse',
    fields={'message': serializers.CharField()},
)


@extend_schema(
    tags=['Auth'],
    summary='درخواست بازیابی رمز عبور',
    description=(
        'ایمیل را بفرستید. اگر حسابی با این ایمیل وجود داشته باشد، لینک بازیابی '
        'برایش ایمیل می‌شود. پاسخ همیشه یکسان است تا وجود حساب لو نرود.'
    ),
    request=ForgotPasswordSerializer,
    responses={200: MessageResponse},
)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ForgotPasswordThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService.request_reset(serializer.validated_data['email'])
        return Response(
            {'message': 'اگر حسابی با این ایمیل وجود داشته باشد، لینک بازیابی رمز عبور برای آن ارسال شد.'},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth'],
    summary='تعیین رمز عبور جدید',
    description='uid و token از لینک ایمیل گرفته می‌شوند. بعد از موفقیت، نشست‌های قبلی (refresh tokenها) باطل می‌شوند.',
    request=ResetPasswordSerializer,
    responses={200: MessageResponse},
)
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ResetPasswordThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService.reset_password(
            serializer.validated_data['user'],
            serializer.validated_data['password'],
        )
        return Response(
            {'message': 'رمز عبور با موفقیت تغییر کرد. با رمز جدید وارد شوید.'},
            status=status.HTTP_200_OK,
        )
