# apps/external_api/urls.py

from django.urls import path
from . import views


urlpatterns = [
    path("keywords/", views.keyword_api, name="monthly_keywords_api"),
    path("books_by_keyword/", views.books_by_keyword_api, name="books_by_keyword_api"),
    path('book_metadata/', views.book_metadata_api, name='book_metadata_api'),
    path('book_description/', views.get_description_api, name='book_description_api'),
    path("recommendation/", views.get_recommendation_api, name='get_recommendation_api'),
    path('check_availability/', views.check_availability_api, name='check_availability_api'),
    path('books_by_agegroup/', views.book_list_by_agegroup_api, name='books_by_agegroup_api'),
    path("bestsellers/", views.bestseller_books_api, name="bestseller_books_api"),
]
