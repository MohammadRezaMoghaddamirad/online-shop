from rest_framework import serializers

from catalog.models import Product

from .models import Cart, CartItem


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "image", "stock")


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    unit_price = serializers.IntegerField(source="product.price", read_only=True)
    line_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity", "unit_price", "line_total")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "items", "total_items", "total_price", "updated_at")

    def get_total_items(self, obj) -> int:
        return obj.get_total_items()

    def get_total_price(self, obj) -> int:
        return obj.get_subtotal()


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """یا quantity (مقدار جدید) یا delta (افزایش/کاهش نسبی، مثلاً +1 یا -1)."""

    quantity = serializers.IntegerField(min_value=1, required=False)
    delta = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if ("quantity" in attrs) == ("delta" in attrs):
            raise serializers.ValidationError("دقیقاً یکی از quantity یا delta را ارسال کنید.")
        return attrs
