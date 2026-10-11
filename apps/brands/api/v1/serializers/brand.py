from rest_framework import serializers
from apps.brands.models import Brand

MAX_LOGO_SIZE = 2 * 1024 * 1024  # ۲ مگابایت


class BrandSerializer(serializers.ModelSerializer):
    """سریالایزر نمایش و ویرایش برند"""

    class Meta:
        model = Brand
        fields = ('id', 'name', 'description', 'logo', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('نام باید حداقل ۲ کاراکتر باشد.')
        return value

    def validate_logo(self, value):
        if value and value.size > MAX_LOGO_SIZE:
            raise serializers.ValidationError('حجم لوگو نباید بیشتر از ۲ مگابایت باشد.')
        return value
