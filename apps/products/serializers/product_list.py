from rest_framework import serializers
from ..models import Product


class ProductListSerializer(serializers.ModelSerializer):
    """Ù†Ù…Ø§ÛŒØ´ Ø®Ù„Ø§ØµÙ‡ Ù…Ø­ØµÙˆÙ„ (Ø¨Ø±Ø§ÛŒ Ù„ÛŒØ³Øª)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'image', 'category', 'category_name',
                  'stock', 'in_stock', 'is_active', 'created_at')
