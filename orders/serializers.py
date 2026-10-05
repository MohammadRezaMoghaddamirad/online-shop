from rest_framework import serializers

from users.models import User

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "unit_price", "quantity", "line_total")


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "status", "total", "items_count", "created_at")

    def get_items_count(self, obj) -> int:
        return len(obj.items.all())


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "status", "items", "subtotal", "discount_amount",
            "shipping_cost", "total", "coupon_code", "created_at", "updated_at",
        )


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class AdminOrderSerializer(OrderSerializer):
    user = UserBriefSerializer(read_only=True)

    class Meta(OrderSerializer.Meta):
        fields = ("user",) + OrderSerializer.Meta.fields


class CheckoutSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(required=False, allow_blank=True)


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
