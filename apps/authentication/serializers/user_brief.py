from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    """Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ø®Ù„Ø§ØµÙ‡ Ú©Ø§Ø±Ø¨Ø±"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'role_display')
