from rest_framework import serializers
from apps.banners.models import Banner

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # ۵ مگابایت


class BannerSerializer(serializers.ModelSerializer):
    """سریالایزر نمایش و ویرایش بنر"""
    is_live = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(default=True)
    
    class Meta:
        model = Banner
        fields = ('id', 'title', 'image', 'link_url', 'position',
                  'sort_order', 'is_active', 'start_at', 'end_at',
                  'is_live', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_image(self, value):
        if value and value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError('حجم تصویر نباید بیشتر از ۵ مگابایت باشد.')
        return value

    def validate(self, attrs):
        # در PATCH ممکن است فقط یکی از دو تاریخ ارسال شود
        start = attrs.get('start_at', getattr(self.instance, 'start_at', None))
        end = attrs.get('end_at', getattr(self.instance, 'end_at', None))
        if start and end and end <= start:
            raise serializers.ValidationError(
                {'end_at': 'تاریخ پایان باید بعد از تاریخ شروع باشد.'}
            )
        return attrs
