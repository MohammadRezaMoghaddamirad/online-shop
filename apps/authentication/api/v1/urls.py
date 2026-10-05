from django.urls import path

from apps.authentication.api.v1.views import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshCustomView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshCustomView.as_view(), name='token-refresh'),
]