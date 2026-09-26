from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from ..models import Coupon
from ..serializers import CouponSerializer
from ..permissions import IsAdmin


class CouponViewSet(viewsets.ModelViewSet):
    """Ù…Ø¯ÛŒØ±ÛŒØª Ú©Ø¯Ù‡Ø§ÛŒ ØªØ®ÙÛŒÙ (ÙÙ‚Ø· Ø§Ø¯Ù…ÛŒÙ†)"""
    queryset = Coupon.objects.all().order_by('-created_at')
    serializer_class = CouponSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'discount_type']
    search_fields = ['code']
    ordering_fields = ['created_at', 'expires_at', 'discount_value']
    ordering = ['-created_at']
