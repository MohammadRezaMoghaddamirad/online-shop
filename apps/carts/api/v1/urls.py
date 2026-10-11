from rest_framework.routers import SimpleRouter

from apps.carts.api.v1.views import CartViewSet

# اسلش پایانی اختیاری است: categories و categories/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('carts', CartViewSet, basename='carts')

urlpatterns = router.urls
