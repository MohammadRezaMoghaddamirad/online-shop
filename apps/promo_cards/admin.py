from django.contrib import admin

from .models import PromoCard


@admin.register(PromoCard)
class PromoCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge_text', 'sort_order', 'is_active', 'created_at')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    ordering = ('sort_order',)
