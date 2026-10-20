from rest_framework import serializers
from apps.banners.models import Banner

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # ۵ مگابایت


class BannerSerializer(serializers.ModelSerializer):
    """سریالایزر نمایش و ویرایش بنر"""
    is_active = serializers.BooleanField(default=True)
    
    class Meta:
        model = Banner
        fields = ('id', 'title', 'image', 'link_url',
                  'sort_order', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_image(self, value):
        if value and value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError('حجم تصویر نباید بیشتر از ۵ مگابایت باشد.')
        return value
