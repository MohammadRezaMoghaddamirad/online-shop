from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..views import OrderViewSet, AdminOrderViewSet

router = DefaultRouter()
router.register('admin', AdminOrderViewSet, basename='admin-orders')
router.register('', OrderViewSet, basename='orders')

urlpatterns = router.urls
