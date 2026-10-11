from rest_framework.routers import SimpleRouter

from apps.orders.api.v1.views import AdminOrderViewSet, OrderViewSet

# اسلش پایانی اختیاری است: categories و categories/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
# admin باید قبل از مسیر detail مشتری (orders/<pk>) ثبت شود
router.register('orders/admin', AdminOrderViewSet, basename='admin-orders')
router.register('orders', OrderViewSet, basename='orders')

urlpatterns = router.urls
