from rest_framework import serializers
from ..models import Product


class StockUpdateSerializer(serializers.ModelSerializer):
    """ÙÙ‚Ø· Ø¨Ø±Ø§ÛŒ ÙˆÛŒØ±Ø§ÛŒØ´ Ù…ÙˆØ¬ÙˆØ¯ÛŒ"""

    class Meta:
        model = Product
        fields = ('stock',)

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ù†Ù…ÛŒâ€ŒØªÙˆØ§Ù†Ø¯ Ù…Ù†ÙÛŒ Ø¨Ø§Ø´Ø¯.')
        return value
