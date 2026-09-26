from rest_framework import serializers
from ..models import Cart
from .cart_item import CartItemSerializer


class CartSerializer(serializers.ModelSerializer):
    """Ù†Ù…Ø§ÛŒØ´ Ú©Ø§Ù…Ù„ Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price',
                  'created_at', 'updated_at')

    def get_total_price(self, obj):
        return obj.total_price

    def get_total_items(self, obj):
        return obj.total_items


class AddToCartSerializer(serializers.Serializer):
    """ÙˆØ±ÙˆØ¯ÛŒ Ø§ÙØ²ÙˆØ¯Ù† Ø¨Ù‡ Ø³Ø¨Ø¯"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """ÙˆØ±ÙˆØ¯ÛŒ ØªØºÛŒÛŒØ± ØªØ¹Ø¯Ø§Ø¯ Ø¢ÛŒØªÙ…"""
    quantity = serializers.IntegerField(min_value=1)
