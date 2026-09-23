from rest_framework import serializers
from ..models import Product
from apps.categories.serializers import CategorySerializer


class ProductDetailSerializer(serializers.ModelSerializer):
    """Ù†Ù…Ø§ÛŒØ´ Ú©Ø§Ù…Ù„ Ù…Ø­ØµÙˆÙ„ + ÙˆÛŒØ±Ø§ÛŒØ´"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.categories.models', fromlist=['Category']).Category.objects.all(),
        source='category',
        write_only=True
    )
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'image',
                  'category', 'category_id', 'stock', 'in_stock',
                  'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Ù‚ÛŒÙ…Øª Ø¨Ø§ÛŒØ¯ Ø¨Ø²Ø±Ú¯ØªØ± Ø§Ø² ØµÙØ± Ø¨Ø§Ø´Ø¯.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ù†Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ø¯ Ù…Ù†ÙÛŒ Ø¨Ø§Ø´Ø¯.')
        return value
