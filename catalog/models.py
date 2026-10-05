from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def sellable(self):
        """محصولات قابل نمایش در فروشگاه: خودش و دسته‌بندی‌اش فعال باشند."""
        return self.filter(is_active=True, category__is_active=True)


class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    price = models.PositiveBigIntegerField(validators=[MinValueValidator(1)], help_text="قیمت به تومان")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    # حذف دسته‌بندی‌ای که محصول دارد مجاز نیست
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0
