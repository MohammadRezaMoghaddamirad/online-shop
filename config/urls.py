from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ============ API v1 ============
api_v1_patterns = [
    path('auth/', include('apps.authentication.api.v1.urls')),
    path('accounts/', include('apps.accounts.api.v1.urls')),
    path('categories/', include('apps.categories.api.v1.urls')),
    path('products/', include('apps.products.api.v1.urls')),
    path('carts/', include('apps.carts.api.v1.urls')),
    path('coupons/', include('apps.coupons.api.v1.urls')),
    path('orders/', include('apps.orders.api.v1.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),

    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)