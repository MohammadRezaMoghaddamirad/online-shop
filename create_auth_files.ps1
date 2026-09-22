# ============================================
# Script to create authentication app files
# ============================================

$basePath = "apps\authentication"

Write-Host "Creating files in $basePath ..." -ForegroundColor Cyan

# -------- apps.py --------
@'
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
'@ | Out-File -FilePath "$basePath\apps.py" -Encoding utf8

# -------- permissions.py --------
@'
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """فقط ادمین‌ها دسترسی دارند"""
    message = 'فقط مدیران دسترسی دارند.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == 'admin')
        )
'@ | Out-File -FilePath "$basePath\permissions.py" -Encoding utf8

# -------- serializers/register.py --------
@'
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """سریالایزر ثبت‌نام کاربر جدید"""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'phone', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'رمزهای عبور یکسان نیستند.'})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.CUSTOMER
        user.save()
        return user
'@ | Out-File -FilePath "$basePath\serializers\register.py" -Encoding utf8

# -------- serializers/login.py --------
@'
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """سریالایزر ورود کاربر"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
'@ | Out-File -FilePath "$basePath\serializers\login.py" -Encoding utf8

# -------- serializers/user_brief.py --------
@'
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    """اطلاعات خلاصه کاربر"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'role_display')
'@ | Out-File -FilePath "$basePath\serializers\user_brief.py" -Encoding utf8

# -------- serializers/__init__.py --------
@'
from .register import RegisterSerializer
from .login import LoginSerializer
from .user_brief import UserBriefSerializer

__all__ = [
    'RegisterSerializer',
    'LoginSerializer',
    'UserBriefSerializer',
]
'@ | Out-File -FilePath "$basePath\serializers\__init__.py" -Encoding utf8

# -------- services/token_service.py --------
@'
from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:
    """سرویس مدیریت توکن‌ها"""

    @staticmethod
    def generate_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def blacklist_token(refresh_token_str):
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
            return True
        except Exception:
            return False
'@ | Out-File -FilePath "$basePath\services\token_service.py" -Encoding utf8

# -------- views/register.py --------
@'
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from ..serializers import RegisterSerializer, UserBriefSerializer
from ..services.token_service import TokenService

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """ثبت‌نام کاربر جدید"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = TokenService.generate_tokens_for_user(user)

        return Response({
            'user': UserBriefSerializer(user).data,
            'refresh': tokens['refresh'],
            'access': tokens['access'],
            'message': 'ثبت‌نام با موفقیت انجام شد.'
        }, status=status.HTTP_201_CREATED)
'@ | Out-File -FilePath "$basePath\views\register.py" -Encoding utf8

# -------- views/login.py --------
@'
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny


class LoginView(TokenObtainPairView):
    """ورود کاربر — دریافت Access و Refresh Token"""
    permission_classes = [AllowAny]
'@ | Out-File -FilePath "$basePath\views\login.py" -Encoding utf8

# -------- views/logout.py --------
@'
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..services.token_service import TokenService


class LogoutView(generics.GenericAPIView):
    """خروج کاربر — blacklist کردن Refresh Token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'فیلد refresh لازم است.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if TokenService.blacklist_token(refresh_token):
            return Response(
                {'detail': 'خروج با موفقیت انجام شد.'},
                status=status.HTTP_205_RESET_CONTENT
            )
        return Response(
            {'detail': 'توکن نامعتبر است.'},
            status=status.HTTP_400_BAD_REQUEST
        )
'@ | Out-File -FilePath "$basePath\views\logout.py" -Encoding utf8

# -------- views/__init__.py --------
@'
from .register import RegisterView
from .login import LoginView
from .logout import LogoutView

__all__ = [
    'RegisterView',
    'LoginView',
    'LogoutView',
]
'@ | Out-File -FilePath "$basePath\views\__init__.py" -Encoding utf8

# -------- urls/v1.py --------
@'
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from ..views import RegisterView, LoginView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
'@ | Out-File -FilePath "$basePath\urls\v1.py" -Encoding utf8

# -------- urls/__init__.py --------
@'
from .v1 import urlpatterns as v1_urls

__all__ = ['v1_urls']
'@ | Out-File -FilePath "$basePath\urls\__init__.py" -Encoding utf8

Write-Host "All files created successfully!" -ForegroundColor Green
Write-Host "Files created:" -ForegroundColor Yellow
Get-ChildItem -Path $basePath -Recurse -File | Select-Object FullName