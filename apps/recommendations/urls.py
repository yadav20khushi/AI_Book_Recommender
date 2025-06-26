# apps/recommendations/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("api/selected_book/", views.selected_book_api, name="selected_book_api"),
    path("api/followup_question/", views.followup_question_api, name="followup_question_api"),
]