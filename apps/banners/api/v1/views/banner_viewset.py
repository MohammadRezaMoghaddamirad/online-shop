from django.db.models import Q
from django.utils import timezone
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
    filterset_fields = ['position', 'is_active']
    search_fields = ['title']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['position', 'sort_order', '-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Banner.objects.all()

        # ادمین همه را می‌بیند. بقیه فقط بنرهای فعالی که الان در بازه نمایش‌اند.
        if not (user.is_authenticated and
                (user.is_superuser or user.role == 'admin')):
            now = timezone.now()
            qs = (
                qs.filter(is_active=True)
                .filter(Q(start_at__isnull=True) | Q(start_at__lte=now))
                .filter(Q(end_at__isnull=True) | Q(end_at__gte=now))
            )

        return qs
