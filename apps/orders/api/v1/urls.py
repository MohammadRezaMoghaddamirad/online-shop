from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.orders.api.v1.views import OrderViewSet, AdminOrderViewSet

router = DefaultRouter()
router.register('admin', AdminOrderViewSet, basename='admin-orders')
router.register('', OrderViewSet, basename='orders')

urlpatterns = router.urls
