# ============================================
# Script to create orders app files
# ============================================

$basePath = "apps\orders"

Write-Host "Creating files in $basePath ..." -ForegroundColor Cyan

# -------- Create directories --------
if (-not (Test-Path "$basePath\serializers")) { mkdir "$basePath\serializers" | Out-Null }
if (-not (Test-Path "$basePath\views"))       { mkdir "$basePath\views" | Out-Null }
if (-not (Test-Path "$basePath\urls"))        { mkdir "$basePath\urls" | Out-Null }

New-Item -Path "$basePath\serializers\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$basePath\views\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$basePath\urls\__init__.py" -ItemType File -Force | Out-Null

# -------- models.py --------
@'
from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.coupons.models import Coupon


class Order(models.Model):
    """سفارش"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=0, default=50000)
    total_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    """آیتم سفارش (snapshot از محصول)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)          # snapshot
    product_price = models.DecimalField(max_digits=12, decimal_places=0)  # snapshot
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.product_price * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
'@ | Out-File -FilePath "$basePath\models.py" -Encoding utf8

# -------- permissions.py --------
@'
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """فقط ادمین"""
    message = 'فقط مدیران دسترسی دارند.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.role == 'admin')
        )
'@ | Out-File -FilePath "$basePath\permissions.py" -Encoding utf8

# -------- serializers/order.py --------
@'
from rest_framework import serializers
from ..models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """آیتم سفارش"""
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price',
                  'quantity', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal


class OrderSerializer(serializers.ModelSerializer):
    """نمایش سفارش"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'coupon', 'subtotal', 'discount_amount',
                  'shipping_cost', 'total_amount', 'status', 'status_display',
                  'items', 'created_at', 'updated_at')
        read_only_fields = (
            'id', 'user', 'subtotal', 'discount_amount',
            'total_amount', 'items', 'created_at', 'updated_at'
        )


class CheckoutSerializer(serializers.Serializer):
    """ورودی Checkout"""
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    shipping_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        required=False,
        default=50000
    )


class OrderStatusSerializer(serializers.ModelSerializer):
    """تغییر وضعیت سفارش (فقط ادمین)"""
    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        valid = [c[0] for c in Order.Status.choices]
        if value not in valid:
            raise serializers.ValidationError('وضعیت نامعتبر است.')
        return value
'@ | Out-File -FilePath "$basePath\serializers\order.py" -Encoding utf8

# -------- serializers/__init__.py --------
@'
from .order import (
    OrderItemSerializer,
    OrderSerializer,
    CheckoutSerializer,
    OrderStatusSerializer,
)

__all__ = [
    'OrderItemSerializer',
    'OrderSerializer',
    'CheckoutSerializer',
    'OrderStatusSerializer',
]
'@ | Out-File -FilePath "$basePath\serializers\__init__.py" -Encoding utf8

# -------- views/order_viewset.py --------
@'
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from ..models import Order, OrderItem
from ..serializers import OrderSerializer, CheckoutSerializer
from apps.carts.models import Cart
from apps.coupons.models import Coupon, CouponUsage


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """سفارش‌های مشتری"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """ثبت سفارش از سبد خرید"""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon_code = serializer.validated_data.get('coupon_code', '').strip()
        shipping_cost = serializer.validated_data.get('shipping_cost', Decimal(50000))

        # سبد خرید
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {'detail': 'سبد خرید خالی است.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            items = list(cart.items.select_related('product').select_for_update())

            # بررسی موجودی
            for item in items:
                if not item.product.is_active:
                    return Response(
                        {'detail': f'محصول {item.product.name} غیرفعال است.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if item.quantity > item.product.stock:
                    return Response(
                        {'detail': f'موجودی {item.product.name} کافی نیست. '
                                   f'(موجودی: {item.product.stock})'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            subtotal = sum(item.subtotal for item in items)
            discount_amount = Decimal(0)
            coupon_obj = None

            # بررسی کد تخفیف
            if coupon_code:
                try:
                    coupon_obj = Coupon.objects.get(code__iexact=coupon_code)
                except Coupon.DoesNotExist:
                    return Response(
                        {'detail': 'کد تخفیف یافت نشد.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                valid, err = coupon_obj.is_valid(order_amount=subtotal, user=request.user)
                if not valid:
                    return Response(
                        {'detail': err},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                discount_amount = coupon_obj.calculate_discount(subtotal)

            total = subtotal - discount_amount + shipping_cost
            if total < 0:
                total = Decimal(0)

            # ساخت سفارش
            order = Order.objects.create(
                user=request.user,
                coupon=coupon_obj,
                subtotal=subtotal,
                discount_amount=discount_amount,
                shipping_cost=shipping_cost,
                total_amount=total,
                status=Order.Status.PENDING,
            )

            # تبدیل CartItem به OrderItem + کاهش موجودی
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                )
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])

            # ثبت استفاده از کد تخفیف
            if coupon_obj:
                CouponUsage.objects.create(
                    coupon=coupon_obj,
                    user=request.user,
                    order=order,
                )

            # خالی کردن سبد
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
'@ | Out-File -FilePath "$basePath\views\order_viewset.py" -Encoding utf8

# -------- views/admin_order_viewset.py --------
@'
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from ..models import Order
from ..serializers import OrderSerializer, OrderStatusSerializer
from ..permissions import IsAdmin


class AdminOrderViewSet(viewsets.ModelViewSet):
    """مدیریت سفارش‌ها (فقط ادمین)"""
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'user']
    ordering_fields = ['created_at', 'total_amount']
    http_method_names = ['get', 'patch', 'head', 'options']

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """تغییر وضعیت سفارش"""
        order = self.get_object()
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
'@ | Out-File -FilePath "$basePath\views\admin_order_viewset.py" -Encoding utf8

# -------- views/__init__.py --------
@'
from .order_viewset import OrderViewSet
from .admin_order_viewset import AdminOrderViewSet

__all__ = ['OrderViewSet', 'AdminOrderViewSet']
'@ | Out-File -FilePath "$basePath\views\__init__.py" -Encoding utf8

# -------- urls/v1.py --------
@'
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..views import OrderViewSet, AdminOrderViewSet

router = DefaultRouter()
router.register('admin', AdminOrderViewSet, basename='admin-orders')
router.register('', OrderViewSet, basename='orders')

urlpatterns = router.urls
'@ | Out-File -FilePath "$basePath\urls\v1.py" -Encoding utf8

# -------- urls/__init__.py --------
@'
from .v1 import urlpatterns as v1_urls

__all__ = ['v1_urls']
'@ | Out-File -FilePath "$basePath\urls\__init__.py" -Encoding utf8

# -------- admin.py --------
@'
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'product_price', 'quantity')
    search_fields = ('product_name', 'order__id')
'@ | Out-File -FilePath "$basePath\admin.py" -Encoding utf8

# -------- apps.py --------
@'
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
'@ | Out-File -FilePath "$basePath\apps.py" -Encoding utf8

Write-Host ""
Write-Host "All files created successfully!" -ForegroundColor Green
Get-ChildItem -Path $basePath -Recurse -File | Select-Object FullName