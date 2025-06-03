# apps/recommendations/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('clova/', views.clova_chat_page, name='clova_chat_page'),
]
