
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from apps.authentication.api.v1.serializers import (
    RegisterSerializer,
    UserBriefSerializer,
)
from apps.authentication.services.token_service import TokenService

User = get_user_model()


@extend_schema(tags=['Auth'])
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