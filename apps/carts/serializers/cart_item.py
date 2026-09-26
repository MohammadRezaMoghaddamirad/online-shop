from rest_framework import serializers
from ..models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Ù†Ù…Ø§ÛŒØ´ Ø¢ÛŒØªÙ… Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=12,
        decimal_places=0,
        read_only=True
    )
    product_image = serializers.ImageField(source='product.image', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_price',
                  'product_image', 'quantity', 'subtotal', 'created_at')

    def get_subtotal(self, obj):
        return obj.subtotal
