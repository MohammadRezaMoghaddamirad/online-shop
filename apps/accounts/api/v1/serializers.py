from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    """سریالایزر ثبت‌نام کاربر جدید"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'رمزهای عبور یکسان نیستند.'})
        return attrs

    def validate_email(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return value

    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.CUSTOMER
        user.save()
        return user


class UserSerializer(serializers.Serializer):
    """نمایش اطلاعات کاربر"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
    role_display = serializers.SerializerMethodField()
    phone = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    def get_role_display(self, obj):
        return obj.get_role_display() if hasattr(obj, 'get_role_display') else obj.role


class ProfileUpdateSerializer(serializers.Serializer):
    """ویرایش پروفایل توسط خود کاربر"""
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AdminUserSerializer(serializers.Serializer):
    """مدیریت کاربران توسط ادمین"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[('customer', 'Customer'), ('admin', 'Admin')])
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        if instance.is_superuser:
            validated_data.pop('role', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance