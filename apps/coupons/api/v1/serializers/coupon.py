from rest_framework import serializers
from apps.coupons.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    """سریالایزر کد تخفیف"""
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
        """کد باید فقط حروف و اعداد باشد"""
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError(
                'کد فقط می‌تواند شامل حروف، اعداد، _ و - باشد.'
            )
        return value.upper()

    def validate(self, attrs):
        """اعتبارسنجی نوع و مقدار تخفیف"""
        discount_type = attrs.get('discount_type')
        discount_value = attrs.get('discount_value')

        if discount_type == Coupon.DiscountType.PERCENT:
            if discount_value > 100:
                raise serializers.ValidationError(
                    {'discount_value': 'درصد تخفیف نمی‌تواند بیشتر از 100 باشد.'}
                )
            if discount_value <= 0:
                raise serializers.ValidationError(
                    {'discount_value': 'درصد تخفیف باید بزرگتر از صفر باشد.'}
                )
        elif discount_type == Coupon.DiscountType.FIXED:
            if discount_value <= 0:
                raise serializers.ValidationError(
                    {'discount_value': 'مبلغ تخفیف باید بزرگتر از صفر باشد.'}
                )

        return attrs
