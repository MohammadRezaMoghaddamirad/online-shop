from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.carts.models import Cart, CartItem
from apps.carts.api.v1.serializers import (
    CartSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)
from apps.products.models import Product
from core.exceptions import BusinessRuleError


class CartViewSet(viewsets.ViewSet):
    """
    مدیریت سبد خرید کاربر جاری.

    تمام اندپوینت‌ها نیاز به احراز هویت (JWT) دارند.
    سبد خرید به صورت خودکار برای هر کاربر ساخته می‌شود.
    """
    permission_classes = [IsAuthenticated]

    def _get_cart(self):
        """
        دریافت یا ساخت سبد خرید برای کاربر جاری.

        Returns:
            Cart: شیء سبد خرید کاربر.
        """
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    # ============================================================
    # GET /carts/  →  مشاهده سبد خرید
    # ============================================================
    @extend_schema(
        tags=['Carts'],
        summary="مشاهده سبد خرید",
        description="سبد خرید کاربر جاری را همراه با آیتم‌ها برمی‌گرداند.",
        responses={200: CartSerializer},
    )
    def list(self, request):
        cart = self._get_cart()
        return Response(CartSerializer(cart).data)

    # ============================================================
    # POST /carts/add/  →  افزودن محصول به سبد
    # ============================================================
    @extend_schema(
        tags=['Carts'],
        summary="افزودن محصول به سبد",
        description=(
            "یک محصول را با تعداد مشخص به سبد اضافه می‌کند. "
            "اگر محصول قبلاً در سبد باشد، تعداد آن افزایش می‌یابد."
        ),
        request=AddToCartSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description='موجودی کافی نیست'),
            404: OpenApiResponse(description='محصول یافت نشد'),
        },
    )
    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        """افزودن محصول به سبد خرید."""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        # ---- بررسی وجود و فعال بودن محصول (و دسته‌بندی آن) ----
        try:
            product = Product.objects.get(
                pk=product_id, is_active=True, category__is_active=True
            )
        except Product.DoesNotExist:
            raise NotFound('محصول یافت نشد یا غیرفعال است.')

        cart = self._get_cart()
        item = cart.items.filter(product=product).first()

        # ---- بررسی موجودی، قبل از ساخت/تغییر آیتم ----
        current_qty = item.quantity if item else 0
        new_qty = current_qty + quantity
        if new_qty > product.stock:
            raise BusinessRuleError(
                f'موجودی کافی نیست. حداکثر موجودی: {product.stock}'
            )

        if item:
            item.quantity = new_qty
            item.save(update_fields=['quantity'])
        else:
            CartItem.objects.create(cart=cart, product=product, quantity=new_qty)

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    # ============================================================
    # PATCH /carts/items/{item_id}/  →  تغییر تعداد آیتم
    # ============================================================
    @extend_schema(
        tags=['Carts'],
        summary="تغییر تعداد آیتم سبد",
        description="تعداد یک آیتم مشخص در سبد خرید را تغییر می‌دهد.",
        parameters=[
            OpenApiParameter(
                name='item_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='شناسه آیتم سبد',
            ),
        ],
        request=UpdateCartItemSerializer,
        responses={
            200: CartSerializer,
            400: OpenApiResponse(description='موجودی کافی نیست'),
            404: OpenApiResponse(description='آیتم یافت نشد'),
        },
    )
    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[0-9]+)')
    def update_item(self, request, item_id=None):
        """تغییر تعداد یک آیتم در سبد خرید."""
        cart = self._get_cart()

        # ---- یافتن آیتم ----
        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            raise NotFound('آیتم یافت نشد.')

        # ---- اعتبارسنجی ورودی ----
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qty = serializer.validated_data['quantity']

        # ---- بررسی موجودی ----
        if qty > item.product.stock:
            raise BusinessRuleError(
                f'موجودی کافی نیست. حداکثر: {item.product.stock}'
            )

        item.quantity = qty
        item.save()
        return Response(CartSerializer(cart).data)

    # ============================================================
    # DELETE /carts/items/{item_id}/remove/  →  حذف آیتم از سبد
    # ============================================================
    @extend_schema(
        tags=['Carts'],
        summary="حذف آیتم از سبد",
        description="یک آیتم مشخص را از سبد خرید حذف می‌کند.",
        parameters=[
            OpenApiParameter(
                name='item_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='شناسه آیتم سبد',
            ),
        ],
        responses={
            200: CartSerializer,
            404: OpenApiResponse(description='آیتم یافت نشد'),
        },
    )
    @action(detail=False, methods=['delete'],
            url_path='items/(?P<item_id>[0-9]+)/remove')
    def remove_item(self, request, item_id=None):
        """حذف یک آیتم از سبد خرید."""
        cart = self._get_cart()

        # ---- یافتن آیتم ----
        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            raise NotFound('آیتم یافت نشد.')

        item.delete()
        return Response(CartSerializer(cart).data)

    # ============================================================
    # DELETE /carts/clear/  →  خالی کردن سبد
    # ============================================================
    @extend_schema(
        tags=['Carts'],
        summary="خالی کردن سبد",
        description="تمام آیتم‌های سبد خرید کاربر جاری را حذف می‌کند.",
        responses={
            204: OpenApiResponse(description='سبد خالی شد (بدون بدنه)'),
        },
    )
    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        """
        خالی کردن کامل سبد خرید.

        طبق استاندارد HTTP، چون پاسخ بدنه ندارد، از status code 204 استفاده می‌شود.
        """
        cart = self._get_cart()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)