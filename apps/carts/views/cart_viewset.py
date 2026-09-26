
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from ..models import Cart, CartItem
from ..serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)
from apps.products.models import Product


class CartViewSet(viewsets.ViewSet):
    """مدیریت سبد خرید"""
    permission_classes = [IsAuthenticated]

    def _get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @extend_schema(
        summary="مشاهده سبد خرید",
        responses={200: CartSerializer},
    )
    def list(self, request):
        cart = self._get_cart()
        return Response(CartSerializer(cart).data)

    @extend_schema(
        summary="افزودن محصول به سبد",
        request=AddToCartSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description='موجودی کافی نیست'),
            404: OpenApiResponse(description='محصول یافت نشد'),
        },
    )
    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'محصول یافت نشد یا غیرفعال است.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = self._get_cart()
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        new_qty = quantity if created else item.quantity + quantity

        if new_qty > product.stock:
            return Response(
                {'detail': f'موجودی کافی نیست. حداکثر موجودی: {product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = new_qty
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="تغییر تعداد آیتم سبد",
        request=UpdateCartItemSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description='موجودی کافی نیست'),
            404: OpenApiResponse(description='آیتم یافت نشد'),
        },
    )
    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        cart = self._get_cart()

        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'آیتم یافت نشد.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qty = serializer.validated_data['quantity']

        if qty > item.product.stock:
            return Response(
                {'detail': f'موجودی کافی نیست. حداکثر: {item.product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = qty
        item.save()
        return Response(CartSerializer(cart).data)

    @extend_schema(
        summary="حذف آیتم از سبد",
        responses={200: CartSerializer, 404: OpenApiResponse(description='آیتم یافت نشد')},
    )
    @action(detail=False, methods=['delete'],
            url_path='items/(?P<item_id>[^/.]+)/remove')
    def remove_item(self, request, item_id=None):
        cart = self._get_cart()

        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'آیتم یافت نشد.'},
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()
        return Response(CartSerializer(cart).data)

    @extend_schema(
        summary="خالی کردن سبد",
        responses={204: OpenApiResponse(description='سبد خالی شد')},
    )
    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        cart = self._get_cart()
        cart.items.all().delete()
        return Response(
            {'detail': 'سبد خرید خالی شد.'},
            status=status.HTTP_204_NO_CONTENT
        )