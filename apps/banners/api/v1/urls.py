from rest_framework.routers import SimpleRouter

from apps.banners.api.v1.views import BannerViewSet

# اسلش پایانی اختیاری است: banners و banners/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('banners', BannerViewSet, basename='banners')

urlpatterns = router.urls
