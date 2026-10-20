from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.banners.models import Banner
from apps.banners.api.v1.serializers import BannerSerializer
from apps.banners.api.v1.permissions import IsAdminOrReadOnly


class BannerViewSet(viewsets.ModelViewSet):
    """مدیریت بنرها"""
    serializer_class = BannerSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', '-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Banner.objects.all()

        # ادمین همه را می‌بیند. بقیه فقط بنرهای فعال.
        if not (user.is_authenticated and
                (user.is_superuser or user.role == 'admin')):
            qs = qs.filter(is_active=True)

        return qs
