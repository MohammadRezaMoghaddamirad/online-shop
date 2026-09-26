from rest_framework import serializers
from ..models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Ø¢ÛŒØªÙ… Ø³ÙØ§Ø±Ø´"""
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price',
                  'quantity', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    """Ù†Ù…Ø§ÛŒØ´ Ø³ÙØ§Ø±Ø´"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'coupon', 'subtotal', 'discount_amount',
                  'shipping_cost', 'total_amount', 'status', 'status_display',
                  'items', 'created_at', 'updated_at')
        read_only_fields = (
            'id', 'user', 'subtotal', 'discount_amount',
            'total_amount', 'items', 'created_at', 'updated_at'
        )


class CheckoutSerializer(serializers.Serializer):
    """ÙˆØ±ÙˆØ¯ÛŒ Checkout"""
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    shipping_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        required=False,
        default=50000
    )


class OrderStatusSerializer(serializers.ModelSerializer):
    """ØªØºÛŒÛŒØ± ÙˆØ¶Ø¹ÛŒØª Ø³ÙØ§Ø±Ø´ (ÙÙ‚Ø· Ø§Ø¯Ù…ÛŒÙ†)"""
    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        valid = [c[0] for c in Order.Status.choices]
        if value not in valid:
            raise serializers.ValidationError('ÙˆØ¶Ø¹ÛŒØª Ù†Ø§Ù…Ø¹ØªØ¨Ø± Ø§Ø³Øª.')
        return value
