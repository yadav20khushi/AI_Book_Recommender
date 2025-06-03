# apps/external_api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('keyword/', views.keyword_page, name='keyword_page'),
    path('age-group/', views.age_group_page, name='age_group_page'),
    path('books/', views.book_list_page, name='book_list_page'),
    path('bestsellers/', views.bestseller_page, name='bestseller_page'),
]
