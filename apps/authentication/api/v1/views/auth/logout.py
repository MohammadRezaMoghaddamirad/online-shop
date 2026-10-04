from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, inline_serializer

from apps.authentication.services.token_service import TokenService


class LogoutView(generics.GenericAPIView):
    """خروج کاربر — blacklist کردن Refresh Token"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='خروج کاربر',
        description='Refresh Token را blacklist می‌کند.',
        request=inline_serializer(
            name='LogoutRequest',
            fields={
                'refresh': serializers.CharField(
                    help_text='Refresh Token کاربر'
                ),
            },
        ),
        responses={
            205: inline_serializer(
                name='LogoutSuccessResponse',
                fields={'detail': serializers.CharField()},
            ),
            400: inline_serializer(
                name='LogoutErrorResponse',
                fields={'detail': serializers.CharField()},
            ),
        },
    )
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