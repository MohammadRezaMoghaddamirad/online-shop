from django.db import transaction
from rest_framework.exceptions import ValidationError

from catalog.models import Product

from .models import Cart, CartItem


def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return Cart.objects.prefetch_related("items__product").get(pk=cart.pk)


def assert_purchasable(product, quantity):
    """قوانین: فعال بودن، موجودی > 0، و تعداد ≤ موجودی."""
    if not product.is_active or not product.category.is_active:
        raise ValidationError({"product": "این محصول در حال حاضر قابل فروش نیست."})
    if product.stock <= 0:
        raise ValidationError({"quantity": "موجودی این محصول تمام شده است."})
    if quantity > product.stock:
        raise ValidationError(
            {"quantity": f"تعداد درخواستی بیشتر از موجودی است (موجودی: {product.stock})."}
        )


@transaction.atomic
def add_to_cart(user, product_id, quantity):
    product = Product.objects.select_related("category").filter(pk=product_id).first()
    if product is None:
        raise ValidationError({"product_id": "محصول یافت نشد."})
    cart, _ = Cart.objects.get_or_create(user=user)
    item = CartItem.objects.filter(cart=cart, product=product).first()
    new_quantity = (item.quantity if item else 0) + quantity
    assert_purchasable(product, new_quantity)
    if item:
        item.quantity = new_quantity
        item.save(update_fields=["quantity"])
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=new_quantity)
    return get_cart(user)


@transaction.atomic
def update_cart_item(item, quantity=None, delta=None):
    new_quantity = quantity if quantity is not None else item.quantity + delta
    if new_quantity < 1:
        raise ValidationError({"quantity": "تعداد باید حداقل ۱ باشد؛ برای حذف از DELETE استفاده کنید."})
    assert_purchasable(item.product, new_quantity)
    item.quantity = new_quantity
    item.save(update_fields=["quantity"])
    return get_cart(item.cart.user)
