from django.urls import path
from django.shortcuts import redirect
from . import views  # your existing signup/login views

urlpatterns = [
    # path("", lambda request: redirect("signup")),
    # path("signup/", views.signup_view, name="signup"),
    # path("login/", views.login_view, name="login"),
    # path("home/", views.home_page_view, name="home_page"),
    # path("returning/", views.returning_user, name="returning_user"),
    # path("signout/", views.signout_view, name="signout"),

    path("api/signup/", views.api_signup, name="signup_api"),
    path("api/login/", views.api_login, name="login_api"),
    path("api/logout/", views.api_logout, name="logout_api"),
    path("api/check-auth/", views.check_auth, name="check_auth_api"),
    path("api/returning/", views.returning_user_api, name="returning_user_api"),
]