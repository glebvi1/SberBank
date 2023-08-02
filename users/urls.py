from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import (AccountView, EmailVerificationView,
                         ForgotPasswordView, RegistrationView,
                         ResetPasswordView, UserLoginView)

app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("account/", AccountView.as_view(), name="account"),

    path("verification_email/<str:email>/<uuid:code>/", EmailVerificationView.as_view(), name="verification_email"),
    path("forgot_password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset_password/<str:email>/<uuid:code>/", ResetPasswordView.as_view(), name="reset_password"),

    path("logout/", LogoutView.as_view(), name="logout"),
]
