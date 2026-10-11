from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.orders.models import Order
from apps.orders.api.v1.serializers import OrderSerializer, OrderStatusSerializer
from apps.orders.services.order_status import change_order_status
from apps.authentication.api.v1.permissions import IsAdmin


class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """مدیریت سفارش‌ها (فقط ادمین)"""
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'user']
    ordering_fields = ['created_at', 'total_amount']

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """تغییر وضعیت سفارش"""
        order = self.get_object()
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = change_order_status(order, serializer.validated_data['status'])
        return Response(OrderSerializer(order).data)
