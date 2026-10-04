from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.carts.models import Cart
from .cart_item import CartItemSerializer


class CartSerializer(serializers.ModelSerializer):
    """نمایش کامل سبد خرید"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price',
                  'created_at', 'updated_at')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_price(self, obj):
        return obj.total_price

    @extend_schema_field(serializers.IntegerField())
    def get_total_items(self, obj):
        return obj.total_items


class AddToCartSerializer(serializers.Serializer):
    """ورودی افزودن به سبد"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """ورودی تغییر تعداد آیتم"""
    quantity = serializers.IntegerField(min_value=1)