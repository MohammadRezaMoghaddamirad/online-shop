from django.db import models


class Banner(models.Model):
    """بنر تبلیغاتی"""

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    link_url = models.URLField(max_length=500, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title