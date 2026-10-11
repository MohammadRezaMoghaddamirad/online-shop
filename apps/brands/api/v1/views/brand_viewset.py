from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.brands.models import Brand
from apps.brands.api.v1.serializers import BrandSerializer
from apps.brands.api.v1.permissions import IsAdminOrReadOnly


class BrandViewSet(viewsets.ModelViewSet):
    """مدیریت برندها"""
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        qs = Brand.objects.all()

        # فقط ادمین همه را می‌بیند؛ مشتری فقط برندهای فعال
        if not (user.is_authenticated and
                (user.is_superuser or user.role == 'admin')):
            qs = qs.filter(is_active=True)

        return qs
