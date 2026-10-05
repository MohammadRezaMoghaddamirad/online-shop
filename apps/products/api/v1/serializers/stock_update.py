from rest_framework import serializers
from apps.products.models import Product


class StockUpdateSerializer(serializers.ModelSerializer):
    """فقط برای ویرایش موجودی"""

    class Meta:
        model = Product
        fields = ('stock',)

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('موجودی نمی‌تواند منفی باشد.')
        return value
