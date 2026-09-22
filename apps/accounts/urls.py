from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProfileView, AdminUserViewSet

router = DefaultRouter()
router.register('users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]