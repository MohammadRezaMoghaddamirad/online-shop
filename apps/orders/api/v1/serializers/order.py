from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """آیتم سفارش"""
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price',
                  'quantity', 'subtotal')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=0))
    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    """نمایش سفارش"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'coupon', 'subtotal', 'discount_amount',
                  'shipping_cost', 'total_amount', 'status', 'status_display',
                  'items', 'created_at', 'updated_at')
        read_only_fields = (
            'id', 'user', 'subtotal', 'discount_amount', 'shipping_cost',
            'total_amount', 'items', 'created_at', 'updated_at'
        )


class CheckoutSerializer(serializers.Serializer):
    """ورودی Checkout"""
    coupon_code = serializers.CharField(required=False, allow_blank=True)


class OrderStatusSerializer(serializers.ModelSerializer):
    """تغییر وضعیت سفارش (فقط ادمین)"""
    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        valid = [c[0] for c in Order.Status.choices]
        if value not in valid:
            raise serializers.ValidationError('وضعیت نامعتبر است.')
        return value