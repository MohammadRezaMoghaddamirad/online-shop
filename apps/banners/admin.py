from django.contrib import admin
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'sort_order', 'is_active',
                    'start_at', 'end_at', 'created_at')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('position', 'is_active')
    search_fields = ('title',)
    ordering = ('position', 'sort_order')
