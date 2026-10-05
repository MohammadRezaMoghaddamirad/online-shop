from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Coupon, CouponUsage


def normalize_code(code):
    return (code or "").strip().upper()


def validate_coupon(code, user, subtotal):
    """کد وجود دارد؟ فعال؟ منقضی نشده؟ حداقل مبلغ؟ قبلاً استفاده نشده؟"""

    def fail(message):
        raise ValidationError({"coupon_code": message})

    coupon = Coupon.objects.filter(code=normalize_code(code)).first()
    if coupon is None:
        fail("کد تخفیف وجود ندارد.")
    if not coupon.is_active:
        fail("کد تخفیف غیرفعال است.")
    if coupon.expires_at <= timezone.now():
        fail("کد تخفیف منقضی شده است.")
    if subtotal < coupon.min_order_amount:
        fail(f"حداقل مبلغ سفارش برای این کد {coupon.min_order_amount:,} تومان است.")
    if CouponUsage.objects.filter(user=user, coupon=coupon).exists():
        fail("شما قبلاً از این کد تخفیف استفاده کرده‌اید.")
    return coupon


def calculate_discount(coupon, subtotal):
    if coupon.discount_type == Coupon.DiscountType.PERCENT:
        discount = subtotal * coupon.value // 100
    else:
        discount = coupon.value
    return min(discount, subtotal)  # تخفیف هرگز از جمع کالاها بیشتر نمی‌شود
