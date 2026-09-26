from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Cart, CartItem
from ..serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)
from apps.products.models import Product


class CartViewSet(viewsets.ViewSet):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯"""
    permission_classes = [IsAuthenticated]

    def _get_cart(self):
        """Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯ Ú©Ø§Ø±Ø¨Ø± Ø±Ø§ Ø¨Ú¯ÛŒØ± ÛŒØ§ Ø¨Ø³Ø§Ø²"""
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request):
        """Ù…Ø´Ø§Ù‡Ø¯Ù‡ Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯"""
        cart = self._get_cart()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        """Ø§ÙØ²ÙˆØ¯Ù† Ù…Ø­ØµÙˆÙ„ Ø¨Ù‡ Ø³Ø¨Ø¯"""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        # Ø¨Ø±Ø±Ø³ÛŒ ÙˆØ¬ÙˆØ¯ Ù…Ø­ØµÙˆÙ„
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Ù…Ø­ØµÙˆÙ„ ÛŒØ§ÙØª Ù†Ø´Ø¯ ÛŒØ§ ØºÛŒØ±ÙØ¹Ø§Ù„ Ø§Ø³Øª.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = self._get_cart()
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        # Ù…Ø­Ø§Ø³Ø¨Ù‡ ØªØ¹Ø¯Ø§Ø¯ Ù†Ù‡Ø§ÛŒÛŒ
        new_qty = quantity if created else item.quantity + quantity

        # Ø¨Ø±Ø±Ø³ÛŒ Ù…ÙˆØ¬ÙˆØ¯ÛŒ
        if new_qty > product.stock:
            return Response(
                {'detail': f'Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ú©Ø§ÙÛŒ Ù†ÛŒØ³Øª. Ø­Ø¯Ø§Ú©Ø«Ø± Ù…ÙˆØ¬ÙˆØ¯ÛŒ: {product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = new_qty
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """ØªØºÛŒÛŒØ± ØªØ¹Ø¯Ø§Ø¯ Ø¢ÛŒØªÙ… Ø³Ø¨Ø¯"""
        cart = self._get_cart()

        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Ø¢ÛŒØªÙ… ÛŒØ§ÙØª Ù†Ø´Ø¯.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qty = serializer.validated_data['quantity']

        if qty > item.product.stock:
            return Response(
                {'detail': f'Ù…ÙˆØ¬ÙˆØ¯ÛŒ Ú©Ø§ÙÛŒ Ù†ÛŒØ³Øª. Ø­Ø¯Ø§Ú©Ø«Ø±: {item.product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = qty
        item.save()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'],
            url_path='items/(?P<item_id>[^/.]+)/remove')
    def remove_item(self, request, item_id=None):
        """Ø­Ø°Ù Ø¢ÛŒØªÙ… Ø§Ø² Ø³Ø¨Ø¯"""
        cart = self._get_cart()

        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Ø¢ÛŒØªÙ… ÛŒØ§ÙØª Ù†Ø´Ø¯.'},
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        """Ø®Ø§Ù„ÛŒ Ú©Ø±Ø¯Ù† Ø³Ø¨Ø¯"""
        cart = self._get_cart()
        cart.items.all().delete()
        return Response(
            {'detail': 'Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯ Ø®Ø§Ù„ÛŒ Ø´Ø¯.'},
            status=status.HTTP_204_NO_CONTENT
        )
