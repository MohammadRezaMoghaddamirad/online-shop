from django.db import models
from apps.categories.models import Category
from django.contrib.postgres.indexes import GinIndex
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Product(models.Model):
    """مدل محصول"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 80},
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    brand = models.ForeignKey(
        'brands.Brand',
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            GinIndex(
                fields=['name'],
                opclasses=['gin_trgm_ops'],
                name='product_name_trgm_idx',
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0