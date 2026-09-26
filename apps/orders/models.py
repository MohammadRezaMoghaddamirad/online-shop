from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.coupons.models import Coupon


class Order(models.Model):
    """Ø³ÙØ§Ø±Ø´"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=0, default=50000)
    total_amount = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    """Ø¢ÛŒØªÙ… Ø³ÙØ§Ø±Ø´ (snapshot Ø§Ø² Ù…Ø­ØµÙˆÙ„)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)          # snapshot
    product_price = models.DecimalField(max_digits=12, decimal_places=0)  # snapshot
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.product_price * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
