from rest_framework.routers import SimpleRouter

from apps.promo_cards.api.v1.views import PromoCardViewSet

# اسلش پایانی اختیاری است: promo-cards و promo-cards/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('promo-cards', PromoCardViewSet, basename='promo-cards')

urlpatterns = router.urls
