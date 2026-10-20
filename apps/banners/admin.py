from django.contrib import admin
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'sort_order', 'is_active', 'created_at')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    ordering = ('sort_order',)
