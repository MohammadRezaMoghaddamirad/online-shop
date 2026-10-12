from django.urls import re_path

from apps.authentication.api.v1.views.auth.login import LoginView
from apps.authentication.api.v1.views.auth.logout import LogoutView
from apps.authentication.api.v1.views.auth.password_reset import (
    ForgotPasswordView,
    ResetPasswordView,
)
from apps.authentication.api.v1.views.auth.register import RegisterView
from apps.authentication.api.v1.views.auth.token_refresh import TokenRefreshCustomView

urlpatterns = [
    re_path(r'^auth/register/?$', RegisterView.as_view(), name='register'),
    re_path(r'^auth/login/?$', LoginView.as_view(), name='login'),
    re_path(r'^auth/logout/?$', LogoutView.as_view(), name='logout'),
    re_path(r'^auth/token/refresh/?$', TokenRefreshCustomView.as_view(), name='token-refresh'),
    re_path(r'^auth/password/forgot/?$', ForgotPasswordView.as_view(), name='password-forgot'),
    re_path(r'^auth/password/reset/?$', ResetPasswordView.as_view(), name='password-reset'),
]
