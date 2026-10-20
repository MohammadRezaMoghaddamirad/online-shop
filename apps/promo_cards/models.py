from django.db import models


class PromoCard(models.Model):
    """کارت تبلیغاتی (Promo Card) برای نمایش در صفحه اصلی فروشگاه"""

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    badge_text = models.CharField(
        max_length=50, blank=True,
        help_text='متن نشان کوچک روی کارت، مثلاً «۲۰٪ تخفیف»',
    )
    image = models.ImageField(upload_to='promo_cards/')
    link_url = models.URLField(max_length=500, blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title
