from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Product
from ..serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    StockUpdateSerializer
)
from ..permissions import IsAdminOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ù…Ø­ØµÙˆÙ„Ø§Øª"""
    queryset = Product.objects.select_related('category').all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at', 'stock']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'update_stock':
            return StockUpdateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Product.objects.select_related('category').all()

        # Ù…Ø´ØªØ±ÛŒØ§Ù† ÙÙ‚Ø· Ù…Ø­ØµÙˆÙ„Ø§Øª ÙØ¹Ø§Ù„ Ø§Ø² Ø¯Ø³ØªÙ‡â€ŒÙ‡Ø§ÛŒ ÙØ¹Ø§Ù„ Ø±Ø§ Ù…ÛŒâ€ŒØ¨ÛŒÙ†Ù†Ø¯
        if not (user.is_authenticated and
                (user.is_superuser or user.role == 'admin')):
            qs = qs.filter(is_active=True, category__is_active=True)

        return qs

    @action(detail=True, methods=['patch'], url_path='stock')
    def update_stock(self, request, pk=None):
        """ÙˆÛŒØ±Ø§ÛŒØ´ Ù…ÙˆØ¬ÙˆØ¯ÛŒ (ÙÙ‚Ø· Ø§Ø¯Ù…ÛŒÙ†)"""
        product = self.get_object()
        serializer = StockUpdateSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
