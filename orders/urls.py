from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import CheckoutView, OrderViewSet

router = SimpleRouter()
router.register("", OrderViewSet, basename="order")

# checkout/ باید قبل از مسیر detail (<pk>/) بیاید
urlpatterns = [path("checkout/", CheckoutView.as_view(), name="checkout")] + router.urls
