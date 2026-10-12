from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.products.models import Product
from apps.products.api.v1.filters import ProductSearchFilter
from apps.products.api.v1.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    StockUpdateSerializer,
)
from apps.products.api.v1.permissions import IsAdminOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    """Product management"""
    queryset = Product.objects.select_related('category', 'brand').all()
    permission_classes = [IsAdminOrReadOnly]
    # ProductSearchFilter must come after OrderingFilter so that ranking by
    # similarity overrides the default ordering.
    filter_backends = [DjangoFilterBackend, OrderingFilter, ProductSearchFilter]
    filterset_fields = ['category', 'brand', 'is_active']
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
        qs = Product.objects.select_related('category', 'brand').all()

        # Customers only see active products from active categories
        if not (user.is_authenticated and
                (user.is_superuser or user.role == 'admin')):
            qs = qs.filter(is_active=True, category__is_active=True)

        return qs

    @action(detail=True, methods=['patch'], url_path='stock')
    def update_stock(self, request, pk=None):
        """Update stock (admin only)"""
        product = self.get_object()
        serializer = StockUpdateSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
