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
    """Ø³ÙØ§Ø±Ø´â€ŒÙ‡Ø§ÛŒ Ù…Ø´ØªØ±ÛŒ"""
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
        """Ø«Ø¨Øª Ø³ÙØ§Ø±Ø´ Ø§Ø² Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯"""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon_code = serializer.validated_data.get('coupon_code', '').strip()
        shipping_cost = serializer.validated_data.get('shipping_cost', Decimal(50000))

        # Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {'detail': 'Ø³Ø¨Ø¯ Ø®Ø±ÛŒØ¯ Ø®Ø§Ù„ÛŒ Ø§Ø³Øª.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            items = list(cart.items.select_related('product').select_for_update())

            # Ø¨Ø±Ø±Ø³ÛŒ Ù…ÙˆØ¬ÙˆØ¯ÛŒ
            for item in items:
                if not item.product.is_active:
                    return Response(
                        {'detail': f'Ù…Ø­ØµÙˆÙ„ {item.product.name} ØºÛŒØ±ÙØ¹Ø§Ù„ Ø§Ø³Øª.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if item.quantity > item.product.stock:
                    return Response(
                        {'detail': f'Ù…ÙˆØ¬ÙˆØ¯ÛŒ {item.product.name} Ú©Ø§ÙÛŒ Ù†ÛŒØ³Øª. '
                                   f'(Ù…ÙˆØ¬ÙˆØ¯ÛŒ: {item.product.stock})'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            subtotal = sum(item.subtotal for item in items)
            discount_amount = Decimal(0)
            coupon_obj = None

            # Ø¨Ø±Ø±Ø³ÛŒ Ú©Ø¯ ØªØ®ÙÛŒÙ
            if coupon_code:
                try:
                    coupon_obj = Coupon.objects.get(code__iexact=coupon_code)
                except Coupon.DoesNotExist:
                    return Response(
                        {'detail': 'Ú©Ø¯ ØªØ®ÙÛŒÙ ÛŒØ§ÙØª Ù†Ø´Ø¯.'},
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

            # Ø³Ø§Ø®Øª Ø³ÙØ§Ø±Ø´
            order = Order.objects.create(
                user=request.user,
                coupon=coupon_obj,
                subtotal=subtotal,
                discount_amount=discount_amount,
                shipping_cost=shipping_cost,
                total_amount=total,
                status=Order.Status.PENDING,
            )

            # ØªØ¨Ø¯ÛŒÙ„ CartItem Ø¨Ù‡ OrderItem + Ú©Ø§Ù‡Ø´ Ù…ÙˆØ¬ÙˆØ¯ÛŒ
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

            # Ø«Ø¨Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ú©Ø¯ ØªØ®ÙÛŒÙ
            if coupon_obj:
                CouponUsage.objects.create(
                    coupon=coupon_obj,
                    user=request.user,
                    order=order,
                )

            # Ø®Ø§Ù„ÛŒ Ú©Ø±Ø¯Ù† Ø³Ø¨Ø¯
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
