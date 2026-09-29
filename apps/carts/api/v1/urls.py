from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.carts.api.v1.views import CartViewSet

router = DefaultRouter()
router.register('', CartViewSet, basename='cart')

urlpatterns = router.urls
