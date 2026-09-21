from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, LogoutView, ProfileView, AdminUserViewSet
)

router = DefaultRouter()
router.register('users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    # احراز هویت
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # پروفایل
    path('profile/', ProfileView.as_view(), name='profile'),

    # مدیریت کاربران (فقط ادمین)
    path('', include(router.urls)),
]