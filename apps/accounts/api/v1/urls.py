from django.urls import re_path
from rest_framework.routers import SimpleRouter

from apps.accounts.api.v1.views import AdminUserViewSet, ProfileView

# اسلش پایانی اختیاری است: categories و categories/ هر دو کار می‌کنند
router = SimpleRouter()
router.trailing_slash = '/?'
router.register('accounts/users', AdminUserViewSet, basename='users')

urlpatterns = [
    re_path(r'^accounts/profile/?$', ProfileView.as_view(), name='profile'),
] + router.urls
