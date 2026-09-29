from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.categories.api.v1.views import CategoryViewSet

router = DefaultRouter()
router.register('', CategoryViewSet, basename='categories')

urlpatterns = router.urls