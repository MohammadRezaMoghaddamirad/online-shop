from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Ø³Ø±ÛŒØ§Ù„Ø§ÛŒØ²Ø± Ø«Ø¨Øªâ€ŒÙ†Ø§Ù… Ú©Ø§Ø±Ø¨Ø± Ø¬Ø¯ÛŒØ¯"""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'phone', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Ø±Ù…Ø²Ù‡Ø§ÛŒ Ø¹Ø¨ÙˆØ± ÛŒÚ©Ø³Ø§Ù† Ù†ÛŒØ³ØªÙ†Ø¯.'})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ø§ÛŒÙ† Ø§ÛŒÙ…ÛŒÙ„ Ù‚Ø¨Ù„Ø§Ù‹ Ø«Ø¨Øª Ø´Ø¯Ù‡ Ø§Ø³Øª.')
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.CUSTOMER
        user.save()
        return user
