from django.urls import path

from . import views

urlpatterns = [
    path("login", views.UserLoginApi.as_view(), name="login"),
    path("register", views.UserRegisterApi.as_view(), name="register"),
    path("register/staff/", views.StaffRegisterApi.as_view(), name="register-staff"),
    path("me", views.UserMeApi.as_view(), name="me"),
    path("users/<str:uuid>/", views.UserDetailView.as_view(), name="user-detail"),
    path("password/reset", views.UserPasswordResetApi.as_view(), name="password-reset"),
    path("code/verify", views.TokenVerifyApi.as_view(), name="code-verify"),
    path("password/new", views.UserSetNewPasswordApi.as_view(), name="password-new"),
    path(
        "activate/account", views.ActivateAccountApi.as_view(), name="activate-account"
    ),
    path("update-user/<str:uid>/", views.UpdateUserView.as_view(), name="update-user"),
]
