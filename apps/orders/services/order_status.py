from django.db import transaction
from django.db.models import F

from apps.coupons.models import CouponUsage
from apps.orders.models import Order
from apps.products.models import Product
from core.exceptions import BusinessRuleError

S = Order.Status

# ─── نقشه تغییرات مجاز وضعیت ───
ALLOWED_TRANSITIONS = {
    S.PENDING:    [S.PAID, S.CANCELLED],
    S.PAID:       [S.PROCESSING, S.CANCELLED],
    S.PROCESSING: [S.SHIPPED, S.CANCELLED],
    S.SHIPPED:    [S.DELIVERED],
    S.DELIVERED:  [],
    S.CANCELLED:  [],
}


@transaction.atomic
def change_order_status(order, new_status):
    """تغییر وضعیت سفارش (order یا pk). لغو سفارش موجودی را برمی‌گرداند و کد تخفیف را آزاد می‌کند."""
    order = Order.objects.select_for_update().get(pk=getattr(order, 'pk', order))

    valid_statuses = [c[0] for c in Order.Status.choices]
    if new_status not in valid_statuses:
        raise BusinessRuleError(f'وضعیت "{new_status}" معتبر نیست.')

    if new_status not in ALLOWED_TRANSITIONS.get(order.status, []):
        raise BusinessRuleError(
            f'تغییر وضعیت از "{order.get_status_display()}" به '
            f'"{dict(Order.Status.choices).get(new_status, new_status)}" مجاز نیست.'
        )

    if new_status == S.CANCELLED:
        for item in order.items.all():
            if item.product_id:
                Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)
        CouponUsage.objects.filter(order=order).delete()

    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    return order
