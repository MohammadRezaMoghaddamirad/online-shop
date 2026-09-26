from rest_framework import serializers
from ..models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """Ø³Ø±ÛŒØ§Ù„Ø§ÛŒØ²Ø± Ú©Ø¯ ØªØ®ÙÛŒÙ"""
    discount_type_display = serializers.CharField(
        source='get_discount_type_display',
        read_only=True
    )

    class Meta:
        model = Coupon
        fields = (
            'id', 'code', 'discount_type', 'discount_type_display',
            'discount_value', 'min_order_amount', 'expires_at',
            'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def validate_code(self, value):
        """Ú©Ø¯ Ø¨Ø§ÛŒØ¯ ÙÙ‚Ø· Ø­Ø±ÙˆÙ Ùˆ Ø§Ø¹Ø¯Ø§Ø¯ Ø¨Ø§Ø´Ø¯"""
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError(
                'Ú©Ø¯ ÙÙ‚Ø· Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ø¯ Ø´Ø§Ù…Ù„ Ø­Ø±ÙˆÙØŒ Ø§Ø¹Ø¯Ø§Ø¯ØŒ _ Ùˆ - Ø¨Ø§Ø´Ø¯.'
            )
        return value.upper()

    def validate(self, attrs):
        """Ø§Ø¹ØªØ¨Ø§Ø±Ø³Ù†Ø¬ÛŒ Ù†ÙˆØ¹ Ùˆ Ù…Ù‚Ø¯Ø§Ø± ØªØ®ÙÛŒÙ"""
        discount_type = attrs.get('discount_type')
        discount_value = attrs.get('discount_value')

        if discount_type == Coupon.DiscountType.PERCENT:
            if discount_value > 100:
                raise serializers.ValidationError(
                    {'discount_value': 'Ø¯Ø±ØµØ¯ ØªØ®ÙÛŒÙ Ù†Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ø¯ Ø¨ÛŒØ´ØªØ± Ø§Ø² 100 Ø¨Ø§Ø´Ø¯.'}
                )
            if discount_value <= 0:
                raise serializers.ValidationError(
                    {'discount_value': 'Ø¯Ø±ØµØ¯ ØªØ®ÙÛŒÙ Ø¨Ø§ÛŒØ¯ Ø¨Ø²Ø±Ú¯ØªØ± Ø§Ø² ØµÙØ± Ø¨Ø§Ø´Ø¯.'}
                )
        elif discount_type == Coupon.DiscountType.FIXED:
            if discount_value <= 0:
                raise serializers.ValidationError(
                    {'discount_value': 'Ù…Ø¨Ù„Øº ØªØ®ÙÛŒÙ Ø¨Ø§ÛŒØ¯ Ø¨Ø²Ø±Ú¯ØªØ± Ø§Ø² ØµÙØ± Ø¨Ø§Ø´Ø¯.'}
                )

        return attrs
