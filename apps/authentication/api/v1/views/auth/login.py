from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, inline_serializer


@extend_schema(
    tags=['Auth'],
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
    },
)
class LoginView(APIView):
    """ورود کاربر — با import تعویقی simplejwt"""
    permission_classes = [AllowAny]

    def post(self, request):
        # ✅ import تعویقی داخل متد
        from rest_framework_simplejwt.views import TokenObtainPairView

        view = TokenObtainPairView.as_view()
        return view(request._request)