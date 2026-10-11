from rest_framework.routers import SimpleRouter

from apps.coupons.api.v1.views import CouponViewSet

# اسلش پایانی اختیاری است: categories و categories/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('coupons', CouponViewSet, basename='coupons')

urlpatterns = router.urls
