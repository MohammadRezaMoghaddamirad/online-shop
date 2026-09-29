from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.coupons.api.v1.views import CouponViewSet

router = DefaultRouter()
router.register('', CouponViewSet, basename='coupons')

urlpatterns = router.urls
