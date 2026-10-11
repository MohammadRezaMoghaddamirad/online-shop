from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """سریالایزر ثبت‌نام: فقط با ایمیل (username خودکار برابر ایمیل می‌شود)"""
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if (User.objects.filter(email__iexact=value).exists()
                or User.objects.filter(username__iexact=value).exists()):
            raise serializers.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'رمزهای عبور یکسان نیستند.'}
            )
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        email = validated_data['email']

        user = User(username=email, role=User.Role.CUSTOMER, **validated_data)
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:  # دو ثبت‌نام همزمان با یک ایمیل
            raise serializers.ValidationError({'email': 'این ایمیل قبلاً ثبت شده است.'})
        return user