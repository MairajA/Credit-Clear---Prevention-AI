from django.urls import path

from credit_clear.users.api.views import LoginView
from credit_clear.users.api.views import LogoutView
from credit_clear.users.api.views import MeView
from credit_clear.users.api.views import PasswordChangeApiView
from credit_clear.users.api.views import PasswordResetConfirmView
from credit_clear.users.api.views import PasswordResetRequestView
from credit_clear.users.api.views import RefreshTokenView
from credit_clear.users.api.views import RegisterView

app_name = "users_api"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("password/change/", PasswordChangeApiView.as_view(), name="password_change"),
    path("password/reset/request/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]
