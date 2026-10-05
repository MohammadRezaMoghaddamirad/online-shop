from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdmin, IsCustomer, IsOwner

from .models import Order
from .serializers import (
    AdminOrderSerializer,
    CheckoutSerializer,
    OrderListSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)
from .services import change_order_status, checkout


class CheckoutView(APIView):
    """POST /api/orders/checkout/ — ثبت سفارش از سبد خرید (کد تخفیف اختیاری)."""

    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(request=CheckoutSerializer, responses={201: OrderSerializer})
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = checkout(request.user, serializer.validated_data.get("coupon_code"))
        order = Order.objects.prefetch_related("items").get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """سفارش‌های خودِ مشتری (لیست و جزئیات)."""

    permission_classes = [IsAuthenticated, IsCustomer, IsOwner]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "total"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    def get_serializer_class(self):
        return OrderListSerializer if self.action == "list" else OrderSerializer


class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin: مشاهده همه‌ی سفارش‌ها، جزئیات و تغییر وضعیت."""

    queryset = Order.objects.select_related("user").prefetch_related("items")
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["status", "user"]
    search_fields = ["user__username", "user__email", "coupon_code"]
    ordering_fields = ["created_at", "total"]
    ordering = ["-created_at"]

    @extend_schema(request=OrderStatusSerializer, responses=AdminOrderSerializer)
    @action(detail=True, methods=["patch"], url_path="status")
    def change_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = change_order_status(order, serializer.validated_data["status"])
        order = self.get_queryset().get(pk=order.pk)
        return Response(AdminOrderSerializer(order).data)
