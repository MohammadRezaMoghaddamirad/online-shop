"""همه‌ی endpointهای پنل مدیریت زیر /api/admin/ ."""
from rest_framework.routers import SimpleRouter

from catalog.views import AdminCategoryViewSet, AdminProductViewSet
from coupons.views import AdminCouponViewSet
from orders.views import AdminOrderViewSet
from users.views import AdminUserViewSet

router = SimpleRouter()
router.register("users", AdminUserViewSet, basename="admin-user")
router.register("categories", AdminCategoryViewSet, basename="admin-category")
router.register("products", AdminProductViewSet, basename="admin-product")
router.register("coupons", AdminCouponViewSet, basename="admin-coupon")
router.register("orders", AdminOrderViewSet, basename="admin-order")

urlpatterns = router.urls
