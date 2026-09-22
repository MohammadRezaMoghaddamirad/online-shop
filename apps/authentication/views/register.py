from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from ..serializers import RegisterSerializer, UserBriefSerializer
from ..services.token_service import TokenService

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ú©Ø§Ø±Ø¨Ø± Ø¬Ø¯ÛŒØ¯"""
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
            'message': 'Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø§Ù†Ø¬Ø§Ù… Ø´Ø¯.'
        }, status=status.HTTP_201_CREATED)
