from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("returning/", views.returning_user_view, name="returning_user"),
]
