from rest_framework.routers import SimpleRouter

from apps.brands.api.v1.views import BrandViewSet

# اسلش پایانی اختیاری است: brands و brands/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('brands', BrandViewSet, basename='brands')

urlpatterns = router.urls
