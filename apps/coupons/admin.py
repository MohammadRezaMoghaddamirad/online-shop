from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value',
                    'min_order_amount', 'expires_at', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)
    ordering = ('-created_at',)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'used_at')
    list_filter = ('coupon',)
    search_fields = ('coupon__code', 'user__username')
