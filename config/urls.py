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
    path('accounts/', include('apps.accounts.urls')),
    path('auth/', include('apps.authentication.urls.v1')),
    path('categories/', include('apps.categories.urls.v1')),
    path('products/', include('apps.products.urls.v1')),
    path('carts/', include('apps.carts.urls.v1')), 
    path('coupons/', include('apps.coupons.urls.v1')),
    # path('orders/', include('apps.orders.urls.v1')),
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