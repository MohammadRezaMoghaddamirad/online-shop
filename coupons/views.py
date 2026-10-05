from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.services import get_cart
from core.permissions import IsAdmin, IsCustomer

from .models import Coupon
from .serializers import CouponSerializer, CouponValidateSerializer
from .services import calculate_discount, validate_coupon


class CouponValidateView(APIView):
    """پیش‌نمایش تخفیف برای سبد فعلی (بدون ثبت سفارش و بدون مصرف کد)."""

    permission_classes = [IsAuthenticated, IsCustomer]

    @extend_schema(
        request=CouponValidateSerializer,
        responses=inline_serializer(
            "CouponPreview",
            {
                "code": serializers.CharField(),
                "subtotal": serializers.IntegerField(),
                "discount_amount": serializers.IntegerField(),
                "total_after_discount": serializers.IntegerField(),
            },
        ),
    )
    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subtotal = get_cart(request.user).get_subtotal()
        coupon = validate_coupon(serializer.validated_data["code"], request.user, subtotal)
        discount = calculate_discount(coupon, subtotal)
        return Response(
            {
                "code": coupon.code,
                "subtotal": subtotal,
                "discount_amount": discount,
                "total_after_discount": subtotal - discount,
            }
        )


class AdminCouponViewSet(viewsets.ModelViewSet):
    """CRUD کد تخفیف؛ فعال/غیرفعال‌سازی با PATCH روی is_active."""

    queryset = Coupon.objects.all().order_by("-created_at")
    serializer_class = CouponSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ["is_active", "discount_type"]
    search_fields = ["code"]
    ordering_fields = ["created_at", "expires_at", "value"]
