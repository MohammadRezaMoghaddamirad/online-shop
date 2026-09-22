from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """سریالایزر ثبت‌نام کاربر جدید"""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'phone', 'address')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'رمزهای عبور یکسان نیستند.'})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.CUSTOMER
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """نمایش اطلاعات کاربر"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'role_display',
                  'phone', 'address', 'is_active', 'date_joined')
        read_only_fields = ('id', 'role', 'is_active', 'date_joined')


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """ویرایش پروفایل توسط خود کاربر"""
    class Meta:
        model = User
        fields = ('email', 'phone', 'address', 'first_name', 'last_name')


class AdminUserSerializer(serializers.ModelSerializer):
    """مدیریت کاربران توسط ادمین"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'address',
                  'is_active', 'is_staff', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'username')