from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "phone", "password", "password_confirm",
        )

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "رمز عبور و تکرار آن یکسان نیستند."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        # نقش همیشه Customer است؛ کاربر نمی‌تواند خودش را Admin کند.
        return User.objects.create_user(role=User.Role.CUSTOMER, **validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "phone", "role", "date_joined",
        )
        read_only_fields = ("id", "username", "role", "date_joined")


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "phone", "role", "is_active", "date_joined",
        )
        read_only_fields = ("id", "username", "email", "first_name", "last_name", "phone", "date_joined")

    def validate(self, attrs):
        request = self.context.get("request")
        if request and self.instance and self.instance.pk == request.user.pk:
            if attrs.get("role", self.instance.role) != self.instance.role or attrs.get("is_active") is False:
                raise serializers.ValidationError("نمی‌توانید نقش یا وضعیت حساب خودتان را تغییر دهید.")
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = ProfileSerializer(self.user).data
        return data
