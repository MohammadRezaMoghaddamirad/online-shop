from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Ø³Ø±ÛŒØ§Ù„Ø§ÛŒØ²Ø± ÙˆØ±ÙˆØ¯ Ú©Ø§Ø±Ø¨Ø±"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
