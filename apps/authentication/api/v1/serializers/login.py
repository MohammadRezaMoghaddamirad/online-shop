from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """سریالایزر ورود کاربر"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
