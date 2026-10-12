from rest_framework import serializers
from apps.products.models import Product


class ProductListSerializer(serializers.ModelSerializer):
    """Short product representation (for lists)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(
        source='brand.name', read_only=True, allow_null=True, default=None
    )
    in_stock = serializers.BooleanField(read_only=True)
    thumbnail = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        url = obj.thumbnail.url
        return request.build_absolute_uri(url) if request else url

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'image', 'thumbnail', 'category',
                  'category_name', 'brand', 'brand_name', 'stock', 'in_stock',
                  'is_active', 'created_at')
