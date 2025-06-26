from django.urls import path
from django.shortcuts import redirect
from . import views  # your existing signup/login views

urlpatterns = [
    path("api/signup/", views.api_signup, name="signup_api"),
    path("api/login/", views.api_login, name="login_api"),
    path("api/logout/", views.api_logout, name="logout_api"),
    path("api/check-auth/", views.check_auth, name="check_auth_api"),
    path("api/returning/", views.returning_user_api, name="returning_user_api"),
]