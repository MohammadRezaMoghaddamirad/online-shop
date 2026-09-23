from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    """سریالایزر نمایش و ویرایش دسته‌بندی"""
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError('نام باید حداقل ۲ کاراکتر باشد.')
        return value