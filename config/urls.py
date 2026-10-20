from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# هر اپ مسیر کامل منبع خودش را دارد (مثلاً categories، categories/<pk>)،
# بنابراین اینجا فقط پیشوند api/v1/ با اسلش گذاشته می‌شود.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.authentication.api.v1.urls')),
    path('api/v1/', include('apps.accounts.api.v1.urls')),
    path('api/v1/', include('apps.categories.api.v1.urls')),
    path('api/v1/', include('apps.brands.api.v1.urls')),
    path('api/v1/', include('apps.banners.api.v1.urls')),
    path('api/v1/', include('apps.products.api.v1.urls')),
    path('api/v1/', include('apps.carts.api.v1.urls')),
    path('api/v1/', include('apps.coupons.api.v1.urls')),
    path('api/v1/', include('apps.orders.api.v1.urls')),
    path('api/v1/', include('apps.promo_cards.api.v1.urls')),

    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
