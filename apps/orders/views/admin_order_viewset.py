from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from ..models import Order
from ..serializers import OrderSerializer, OrderStatusSerializer
from ..permissions import IsAdmin


class AdminOrderViewSet(viewsets.ModelViewSet):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ø³ÙØ§Ø±Ø´â€ŒÙ‡Ø§ (ÙÙ‚Ø· Ø§Ø¯Ù…ÛŒÙ†)"""
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'user']
    ordering_fields = ['created_at', 'total_amount']
    http_method_names = ['get', 'patch', 'head', 'options']

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """ØªØºÛŒÛŒØ± ÙˆØ¶Ø¹ÛŒØª Ø³ÙØ§Ø±Ø´"""
        order = self.get_object()
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
