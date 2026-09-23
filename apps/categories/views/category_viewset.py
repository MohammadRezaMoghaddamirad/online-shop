from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Category
from ..serializers import CategorySerializer
from ..permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """مدیریت دسته‌بندی‌ها"""
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        qs = Category.objects.all()

        # فقط ادمین همه را می‌بیند (فعال و غیرفعال)
        # مشتری فقط دسته‌های فعال را می‌بیند
        if not (user.is_authenticated and
                (user.is_superuser or user.role == 'admin')):
            qs = qs.filter(is_active=True)

        return qs