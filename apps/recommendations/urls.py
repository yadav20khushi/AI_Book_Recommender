# apps/recommendations/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('selected-book/', views.selected_book, name='selected_book'),
    path('followup-question/', views.followup_question, name='followup_question'),
    path("recommendation-type/", views.handle_recommendation_type, name="handle_recommendation_type"),
    path("check-availability/", views.check_availability_view, name="check_availability"),
]
