from django.urls import path
from django.shortcuts import redirect
from . import views  # your existing signup/login views

urlpatterns = [
    path("", lambda request: redirect("signup")),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("home/", views.home_page_view, name="home_page"),
    path("returning/", views.returning_user, name="returning_user"),
    path("signout/", views.signout_view, name="signout"),
]
