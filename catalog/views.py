from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from core.permissions import IsAdmin

from .filters import AdminProductFilter, ProductFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


# ---------------------------- بخش مشتری (فقط خواندنی) ----------------------------
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """لیست دسته‌بندی‌های فعال و محصولات هر دسته."""

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def products(self, request, pk=None):
        """GET /api/categories/{id}/products/ — محصولات قابل فروش یک دسته."""
        category = self.get_object()
        queryset = (
            Product.objects.sellable()
            .filter(category=category)
            .select_related("category")
            .order_by("-created_at")
        )
        page = self.paginate_queryset(queryset)
        serializer = ProductSerializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """لیست/جزئیات محصولات؛ فیلتر، جستجو و مرتب‌سازی بر اساس قیمت."""

    queryset = Product.objects.sellable().select_related("category")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filterset_class = ProductFilter
    search_fields = ["name"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]


# ---------------------------- بخش مدیریت (Admin) ----------------------------
class AdminCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class AdminProductViewSet(viewsets.ModelViewSet):
    """CRUD محصولات؛ تغییر موجودی و فعال/غیرفعال‌سازی با PATCH روی stock و is_active."""

    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin]
    filterset_class = AdminProductFilter
    search_fields = ["name"]
    ordering_fields = ["price", "created_at", "name", "stock"]
    ordering = ["-created_at"]
