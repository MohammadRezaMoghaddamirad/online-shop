from django.db import models
from django.utils import timezone


class Banner(models.Model):
    """بنر تبلیغاتی (اسلایدر صفحه اصلی و ...)"""

    class Position(models.TextChoices):
        HOME_MAIN = 'home_main', 'Home main'
        HOME_SIDE = 'home_side', 'Home side'
        CATEGORY = 'category', 'Category'

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    link_url = models.URLField(max_length=500, blank=True)
    position = models.CharField(
        max_length=20,
        choices=Position.choices,
        default=Position.HOME_MAIN,
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'sort_order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_live(self):
        """آیا بنر همین الان باید نمایش داده شود؟"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_at and self.start_at > now:
            return False
        if self.end_at and self.end_at < now:
            return False
        return True
