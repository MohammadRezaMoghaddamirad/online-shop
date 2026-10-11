from rest_framework import serializers
from apps.products.models import Product


class ProductListSerializer(serializers.ModelSerializer):
    """نمایش خلاصه محصول (برای لیست)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(
        source='brand.name', read_only=True, allow_null=True, default=None
    )
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'image', 'category', 'category_name',
                  'brand', 'brand_name', 'stock', 'in_stock', 'is_active', 'created_at')
