from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.promo_cards.api.v1.permissions import IsAdminOrReadOnly
from apps.promo_cards.api.v1.serializers import PromoCardSerializer
from apps.promo_cards.models import PromoCard


class PromoCardViewSet(viewsets.ModelViewSet):
    """مدیریت کارت‌های تبلیغاتی"""
    serializer_class = PromoCardSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title', 'subtitle']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order', '-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = PromoCard.objects.all()

        # ادمین همه را می‌بیند. بقیه فقط کارت‌های فعال.
        if not (user.is_authenticated and
                (user.is_superuser or user.role == 'admin')):
            qs = qs.filter(is_active=True)

        return qs
