
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    """کد تخفیف"""
    class DiscountType(models.TextChoices):
        PERCENT = 'percent', 'Percent'
        FIXED = 'fixed', 'Fixed'

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=12, decimal_places=0)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self, order_amount=None, user=None):
        """بررسی اعتبار کد"""
        if not self.is_active:
            return False, 'کد تخفیف غیرفعال است.'

        if self.expires_at < timezone.now():
            return False, 'کد تخفیف منقضی شده است.'

        if order_amount is not None and order_amount < self.min_order_amount:
            return False, f'حداقل مبلغ سفارش {self.min_order_amount} تومان است.'

        if user is not None:
            if CouponUsage.objects.filter(coupon=self, user=user).exists():
                return False, 'این کد قبلاً توسط شما استفاده شده است.'

        return True, None

    def calculate_discount(self, amount):
        """محاسبه مقدار تخفیف"""
        if self.discount_type == self.DiscountType.PERCENT:
            return (amount * self.discount_value) / 100
        return min(self.discount_value, amount)


class CouponUsage(models.Model):
    """استفاده از کد تخفیف"""
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('coupon', 'user')

    def __str__(self):
        return f"{self.coupon.code} - {self.user.username}"