from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.api.v1.serializers import (
    UserSerializer, ProfileUpdateSerializer, AdminUserSerializer
)
from apps.authentication.api.v1.permissions import IsAdmin
from core.exceptions import BusinessRuleError


class ProfileView(generics.RetrieveUpdateAPIView):
    """مشاهده و ویرایش پروفایل کاربر لاگین‌شده"""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ProfileUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(instance).data)


class AdminUserViewSet(viewsets.ModelViewSet):
    """مدیریت کاربران توسط ادمین"""
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'patch', 'head', 'options']  # حذف/PUT کاربر لازم نیست (سفارش‌ها PROTECT هستند)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'phone']
    ordering_fields = ['date_joined', 'username']

    def get_queryset(self):
        # ✅ import تعویقی داخل متد
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.all().order_by('-date_joined')

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        is_deactivating = str(request.data.get('is_active', '')).lower() in ('false', '0')
        if instance.pk == request.user.pk and ('role' in request.data or is_deactivating):
            raise BusinessRuleError('نمی‌توانید نقش یا وضعیت حساب خودتان را تغییر دهید.')
        if instance.is_superuser and 'role' in request.data:
            raise BusinessRuleError('نقش سوپر‌یوزر قابل تغییر نیست.')
        return super().partial_update(request, *args, **kwargs)