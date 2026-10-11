from rest_framework.routers import SimpleRouter

from apps.products.api.v1.views import ProductViewSet

# اسلش پایانی اختیاری است: categories و categories/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('products', ProductViewSet, basename='products')

urlpatterns = router.urls
