from rest_framework.routers import SimpleRouter

from apps.categories.api.v1.views import CategoryViewSet

# اسلش پایانی اختیاری است: categories و categories/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('categories', CategoryViewSet, basename='categories')

urlpatterns = router.urls
