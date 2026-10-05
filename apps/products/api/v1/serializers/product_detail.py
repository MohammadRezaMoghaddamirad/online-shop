from rest_framework import serializers
from apps.products.models import Product
from apps.categories.api.v1.serializers import CategorySerializer


class ProductDetailSerializer(serializers.ModelSerializer):
    """نمایش کامل محصول + ویرایش"""
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
            raise serializers.ValidationError('قیمت باید بزرگتر از صفر باشد.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('موجودی نمی‌تواند منفی باشد.')
        return value
