from rest_framework import serializers

from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            "id", "code", "discount_type", "value", "min_order_amount",
            "expires_at", "is_active", "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        discount_type = attrs.get("discount_type", getattr(self.instance, "discount_type", None))
        value = attrs.get("value", getattr(self.instance, "value", None))
        if value is not None and value <= 0:
            raise serializers.ValidationError({"value": "مقدار تخفیف باید بزرگ‌تر از صفر باشد."})
        if discount_type == Coupon.DiscountType.PERCENT and value is not None and value > 100:
            raise serializers.ValidationError({"value": "تخفیف درصدی نمی‌تواند بیشتر از ۱۰۰ باشد."})
        return attrs


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField()
