from rest_framework import serializers

from apps.promo_cards.models import PromoCard

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # ۵ مگابایت


class PromoCardSerializer(serializers.ModelSerializer):
    """سریالایزر نمایش و ویرایش کارت تبلیغاتی"""
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = PromoCard
        fields = ('id', 'title', 'subtitle', 'badge_text', 'image',
                  'link_url', 'button_text', 'sort_order', 'is_active',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_image(self, value):
        if value and value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError('حجم تصویر نباید بیشتر از ۵ مگابایت باشد.')
        return value
