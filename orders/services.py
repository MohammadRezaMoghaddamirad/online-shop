from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from cart.models import Cart
from catalog.models import Product
from coupons.models import CouponUsage
from coupons.services import calculate_discount, validate_coupon

from .models import Order, OrderItem

S = Order.Status

# گذارهای مجاز وضعیت سفارش
ALLOWED_TRANSITIONS = {
    S.PENDING: {S.PAID, S.CANCELLED},
    S.PAID: {S.PROCESSING, S.CANCELLED},
    S.PROCESSING: {S.SHIPPED, S.CANCELLED},
    S.SHIPPED: {S.DELIVERED},
    S.DELIVERED: set(),
    S.CANCELLED: set(),
}


@transaction.atomic
def checkout(user, coupon_code=None):
    """ثبت سفارش از روی سبد خرید (همه‌ی مراحل در یک تراکنش)."""
    cart = Cart.objects.filter(user=user).first()
    cart_items = list(cart.items.all()) if cart else []
    if not cart_items:
        raise ValidationError({"cart": ["سبد خرید خالی است."]})

    # قفل ردیف محصولات (به ترتیب id برای جلوگیری از deadlock) تا خریدهای همزمان موجودی را منفی نکنند
    product_ids = sorted({item.product_id for item in cart_items})
    products = {
        p.id: p
        for p in Product.objects.select_related("category")
        .select_for_update(of=("self",))
        .filter(id__in=product_ids)
        .order_by("id")
    }

    # 1) بررسی محصولات و موجودی
    errors = []
    for item in cart_items:
        product = products.get(item.product_id)
        if product is None or not product.is_active or not product.category.is_active:
            name = product.name if product else f"#{item.product_id}"
            errors.append(f"محصول «{name}» در حال حاضر قابل فروش نیست.")
        elif product.stock <= 0:
            errors.append(f"موجودی محصول «{product.name}» تمام شده است.")
        elif item.quantity > product.stock:
            errors.append(
                f"تعداد درخواستی «{product.name}» بیشتر از موجودی است (موجودی: {product.stock})."
            )
    if errors:
        raise ValidationError({"cart": errors})

    # 2) محاسبه مبلغ
    subtotal = sum(products[i.product_id].price * i.quantity for i in cart_items)

    coupon, discount = None, 0
    if coupon_code:
        coupon = validate_coupon(coupon_code, user, subtotal)
        discount = calculate_discount(coupon, subtotal)

    shipping_cost = settings.SHOP_SHIPPING_COST
    total = subtotal - discount + shipping_cost

    # 3) ساخت سفارش و OrderItem (با snapshot قیمت و نام)
    order = Order.objects.create(
        user=user,
        subtotal=subtotal,
        discount_amount=discount,
        shipping_cost=shipping_cost,
        total=total,
        coupon_code=coupon.code if coupon else "",
    )
    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                product=products[i.product_id],
                product_name=products[i.product_id].name,
                unit_price=products[i.product_id].price,
                quantity=i.quantity,
            )
            for i in cart_items
        ]
    )

    # 4) کم کردن موجودی
    for item in cart_items:
        product = products[item.product_id]
        product.stock -= item.quantity
        product.save(update_fields=["stock", "updated_at"])

    # 5) ثبت مصرف کد تخفیف (قید یکتا جلوی مصرف همزمان دوباره را می‌گیرد)
    if coupon:
        try:
            with transaction.atomic():
                CouponUsage.objects.create(user=user, coupon=coupon, order=order)
        except IntegrityError:
            raise ValidationError({"coupon_code": "شما قبلاً از این کد تخفیف استفاده کرده‌اید."})

    # 6) خالی کردن سبد
    cart.items.all().delete()
    return order


@transaction.atomic
def change_order_status(order, new_status):
    order = Order.objects.select_for_update().get(pk=order.pk)

    if new_status == order.status:
        raise ValidationError({"status": "سفارش از قبل در همین وضعیت است."})
    if new_status not in ALLOWED_TRANSITIONS[order.status]:
        raise ValidationError(
            {"status": f"تغییر وضعیت از «{order.status}» به «{new_status}» مجاز نیست."}
        )

    if new_status == S.CANCELLED:
        # برگرداندن موجودی و آزاد کردن کد تخفیف
        for item in order.items.all():
            if item.product_id:
                Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
        CouponUsage.objects.filter(order=order).delete()

    order.status = new_status
    order.save(update_fields=["status", "updated_at"])
    return order
