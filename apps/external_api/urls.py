# apps/external_api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('keyword/', views.keyword_page, name='keyword_page'),
    path('age-group/', views.age_group_page, name='age_group_page'),
    path('age-group/books/', views.book_list_by_agegroup, name='book_list_by_agegroup'),
    path('keyword/books/', views.books_by_keyword, name='book_list_by_keyword'),
    path('books/by-keyword/', views.books_by_keyword, name='book_list_by_keyword'),
    path('bestsellers/', views.bestseller_page, name='bestseller_page'),
]
